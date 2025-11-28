import json
import random
from pathlib import Path
from urllib.parse import quote

from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Base folders
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
STATIC_DIR = REPO_ROOT / "static"
COMP_DIR = STATIC_DIR / "components"
DATA_DIR = REPO_ROOT / "mcq" / "quiz" / "data"
MISTAKES_PATH = DATA_DIR / "mistakes.json"


# ---------- Helpers to support existing static UI ----------

def _read_text(p: Path, default: str = "") -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def _normalize_questions(raw):
    """Accept list of question dicts and normalize to structure used by UI."""
    def _fix_mojibake(val):
        if not isinstance(val, str):
            return val
        if "â" in val or "�" in val:
            try:
                fixed = val.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
                if fixed and fixed != val:
                    return fixed
            except Exception:
                pass
        return val

    data = raw
    norm = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for q in data:
        opts = q.get("options", q.get("choices", []))
        correct = q.get("correct_answer", q.get("answer", q.get("answerIndex", "")))

        if isinstance(opts, dict):
            items = [(k, _fix_mojibake(opts[k])) for k in sorted(opts.keys(), key=lambda x: str(x))]
            if isinstance(correct, int):
                if 0 <= correct < len(items):
                    correct = items[correct][0]
                else:
                    correct = ""
        else:
            items = [(letters[i], _fix_mojibake(v)) for i, v in enumerate(list(opts))]
            if isinstance(correct, int):
                if 0 <= correct < len(items):
                    correct = items[correct][0]
                else:
                    correct = ""

        norm.append({
            "id": str(q.get("id", q.get("qid", random.randint(1, 10_000)))) ,
            "model": q.get("model", ""),
            "topic": q.get("topic", ""),
            "difficulty": q.get("difficulty", ""),
            "stem": _fix_mojibake(q.get("stem", q.get("text", q.get("q", "")))),
            "items": items,
            "correct": str(correct).strip(),
            "explanation": _fix_mojibake(q.get("explanation", "")),
        })
        # light shuffle to mimic original behavior
        item = norm.pop()
        idx = random.randint(0, len(norm))
        norm.insert(idx, item)
    return norm


def _list_json_files():
    if not STATIC_DIR.exists():
        return []
    return sorted([p.name for p in STATIC_DIR.glob("*.json")])


# ---------- Views ----------

def home(request):
    files = _list_json_files()
    # Load mistakes count if available
    mistakes_count = 0
    try:
        if MISTAKES_PATH.exists():
            txt = MISTAKES_PATH.read_text(encoding="utf-8").strip()
            if txt:
                data = json.loads(txt)
                if isinstance(data, list):
                    mistakes_count = len(data)
    except Exception:
        mistakes_count = 0

    ctx = {
        "files": [{"name": f, "url": f"/play/{quote(f)}"} for f in files],
        "mistakes_count": mistakes_count,
    }
    return render(request, "quiz/home.html", ctx)


def play(request, fname: str):
    json_path = STATIC_DIR / fname
    if not json_path.exists() or json_path.suffix.lower() != ".json":
        raise Http404("JSON not found")

    raw = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "questions" in raw:
        raw = raw["questions"]
    questions = _normalize_questions(raw)
    # Randomize question order each play
    random.shuffle(questions)
    # Build a map of questions for client-side mistake reporting
    qmap = {q["id"]: q for q in questions}

    css = _read_text(COMP_DIR / "style.css")
    outcome_html = _read_text(COMP_DIR / "outcome.html") or (
        "<div class=\"result-card pending\" id=\"outcomeCard\"><h3 data-role=\"status\">PENDING</h3></div>"
    )
    title = json_path.stem

    return render(
        request,
        "quiz/player.html",
        {
            "title": title,
            "css": css,
            "outcome": outcome_html,
            "questions": questions,
            "questions_json": json.dumps(qmap),
        },
    )


# ---------- Legacy single-question trainer (kept under /legacy/) ----------

# Load legacy questions once at import
LEGACY_QUESTIONS_PATH = THIS_DIR / "questions.json"
if LEGACY_QUESTIONS_PATH.exists():
    LEGACY_QUESTIONS = json.loads(LEGACY_QUESTIONS_PATH.read_text(encoding="utf-8"))
else:
    LEGACY_QUESTIONS = []


def _init_session(s):
    s.setdefault("streak", 0)
    s.setdefault("correct", 0)
    s.setdefault("answered", 0)
    if LEGACY_QUESTIONS and ("order" not in s or not s["order"]):
        s["order"] = list(range(len(LEGACY_QUESTIONS)))
        random.shuffle(s["order"])
        s["idx"] = 0
    s.setdefault("feedback", "")


def _current_question(s):
    return LEGACY_QUESTIONS[s["order"][s["idx"]]]


@require_http_methods(["GET", "POST"])
def mcq(request):
    if not LEGACY_QUESTIONS:
        return redirect("home")
    _init_session(request.session)
    s = request.session

    if request.method == "POST":
        q = _current_question(s)
        chosen = request.POST.get("choice")
        try:
            chosen_idx = int(chosen)
        except (TypeError, ValueError):
            s["feedback"] = "Pick an option."
            request.session.modified = True
            return redirect("mcq")

        s["answered"] += 1
        if chosen_idx == q.get("answerIndex"):
            s["streak"] += 1
            s["correct"] += 1
            s["feedback"] = "Correct."
        else:
            s["streak"] = 0
            ans_idx = q.get("answerIndex", 0)
            choices = q.get("choices", [])
            s["feedback"] = f"Wrong. Answer: {choices[ans_idx] if 0 <= ans_idx < len(choices) else ''}"
            # Append mistake in normalized shape
            try:
                norm_q = _normalize_questions([q])[0]
                _append_mistake(norm_q)
            except Exception:
                pass
        s["idx"] += 1
        if s["idx"] >= len(s["order"]):
            random.shuffle(s["order"])
            s["idx"] = 0
        request.session.modified = True
        return redirect("mcq")

    q = _current_question(s)
    ctx = {
        "qtext": q.get("q", ""),
        "choices": list(enumerate(q.get("choices", []))),
        "stats": {"streak": s["streak"], "correct": s["correct"], "answered": s["answered"]},
        "feedback": s.pop("feedback", ""),
    }
    request.session.modified = True
    return render(request, "quiz/mcq.html", ctx)


def reset(request):
    for k in ["streak", "correct", "answered", "order", "idx", "feedback"]:
        request.session.pop(k, None)
    return redirect("mcq")


# ---------- Mistakes capture and review ----------

def _append_mistake(obj: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    try:
        if MISTAKES_PATH.exists():
            txt = MISTAKES_PATH.read_text(encoding="utf-8").strip()
            if txt:
                data = json.loads(txt)
                if isinstance(data, list):
                    items = data
    except Exception:
        items = []
    items.append(obj)
    MISTAKES_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


@csrf_exempt
@require_http_methods(["POST"])
def api_mistake(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        if not isinstance(payload, dict):
            return JsonResponse({"ok": False, "error": "invalid payload"}, status=400)
        # Expecting normalized question shape from client
        _append_mistake(payload)
        return JsonResponse({"ok": True})
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)


def mistakes(request):
    css = _read_text(COMP_DIR / "style.css")
    outcome_html = _read_text(COMP_DIR / "outcome.html") or (
        "<div class=\"result-card pending\" id=\"outcomeCard\"><h3 data-role=\"status\">PENDING</h3></div>"
    )
    title = "Mistakes"
    try:
        raw = json.loads(MISTAKES_PATH.read_text(encoding="utf-8")) if MISTAKES_PATH.exists() else []
    except Exception:
        raw = []

    # raw is expected to already be normalized question dicts
    # Randomize mistakes order as well
    random.shuffle(raw)
    qmap = {str(q.get("id", i)): q for i, q in enumerate(raw)}
    return render(
        request,
        "quiz/player.html",
        {
            "title": title,
            "css": css,
            "outcome": outcome_html,
            "questions": raw,
            "questions_json": json.dumps(qmap),
        },
    )
