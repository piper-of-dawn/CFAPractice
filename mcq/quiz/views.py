import json
import os
import random
import urllib.request
import urllib.parse
from pathlib import Path

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def _choose_data_path() -> Path:
    base = Path(__file__).resolve().parent / "data"
    # Try Windows-safe underscore version first, then original with colons, then a generic fallback.
    candidates = [
        base / "Module 6_ Fixed-Income Bond Valuation_ Prices and Yields.json",
        base / "Module 6: Fixed-Income Bond Valuation: Prices and Yields.json",
        base / "questions.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    # If nothing found, raise a clear error with the directory listing to aid debugging.
    available = ", ".join(sorted(str(p) for p in base.glob("*.json")))
    raise FileNotFoundError(f"No quiz JSON found in {base}. Available: {available}")


DATA_DIR = Path(__file__).resolve().parent / "data"
MISTAKES_PATH = DATA_DIR / "mistakes.json"
DATA_PATH = _choose_data_path()


def load_questions():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _fix_mojibake(val):
    """Attempt to repair common UTF-8/Windows-1252 mojibake (â€™ â€“ â€œ â€ etc.).
    If suspicious characters are present, try latin1->utf-8 re-decode.
    """
    if not isinstance(val, str):
        return val
    if "â" in val or "�" in val or "€" in val:
        try:
            fixed = val.encode("latin1", errors="ignore").decode(
                "utf-8", errors="ignore"
            )
            if fixed and fixed != val:
                return fixed
        except Exception:
            pass
    return val


def _normalize_questions(raw):
    def norm_one(q):
        # Text/stem
        text = _fix_mojibake(q.get("text") or q.get("stem") or q.get("question") or "")

        # Choices and answer index
        choices = []
        answer_idx = 0

        if isinstance(q.get("choices"), list) and q.get("choices"):
            choices = [_fix_mojibake(x) for x in list(q["choices"])]  # copy
            # Prefer explicit integer index
            if isinstance(q.get("answer"), int):
                answer_idx = int(q["answer"])
            else:
                # Try map from letter if present
                letter = (q.get("answer_letter") or "").strip().upper().rstrip(".")
                if (
                    letter in choices and False
                ):  # placeholder to keep branch structure readable
                    pass
        elif isinstance(q.get("options"), dict) and q.get("options"):
            opts = q["options"]
            # Keep alphabetical A..Z ordering for stable UI
            letters = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c in opts]
            choices = [_fix_mojibake(opts[k]) for k in letters]
            # Derive answer index from a letter-like field
            ans_letter = (
                (q.get("correct_answer") or q.get("answer_letter") or "")
                .strip()
                .upper()
            )
            ans_letter = ans_letter.rstrip(".")
            if ans_letter in letters:
                answer_idx = letters.index(ans_letter)
            else:
                # Fallback to provided index if any
                if isinstance(q.get("answer"), int):
                    answer_idx = int(q["answer"]) or 0
                else:
                    answer_idx = 0
        else:
            # Last resort fallbacks
            choices = [_fix_mojibake(x) for x in list(q.get("choices") or [])]
            answer_idx = int(q.get("answer") or 0)

        # Explanation/rationale if present
        explanation = _fix_mojibake(
            q.get("explanation") or q.get("explanations") or q.get("rationale")
        )

        # Minimal extras to avoid dumping full JSON into UI
        keep = {"id", "topic", "model", "category", "difficulty"}
        extras = {k: v for k, v in q.items() if k in keep}

        return {
            "text": text,
            "choices": choices,
            "answer": answer_idx,
            "explanation": explanation,
            "extras": extras,
        }

    if isinstance(raw, list):
        return [norm_one(q) for q in raw]
    # If file contains an object that wraps a list, try common keys
    for key in ("questions", "items", "data"):
        if isinstance(raw, dict) and isinstance(raw.get(key), list):
            return [norm_one(q) for q in raw[key]]
    raise ValueError("Unsupported quiz JSON structure: expected a list of questions")


QUESTIONS = _normalize_questions(load_questions())


def _score_and_streak(answers):
    # answers: list[bool] indicating correctness per question
    score = sum(1 for a in answers if a)
    # current streak: consecutive correct answers at the end
    streak = 0
    for a in reversed(answers):
        if a:
            streak += 1
        else:
            break
    # longest streak (for display if needed)
    longest = 0
    cur = 0
    for a in answers:
        if a:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    return score, streak, longest


def _upstash_cfg():
    url = os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    if url and token:
        return url.rstrip("/"), token
    return None, None


def _upstash_call(command: str, *args: str):
    # Use simple REST form: /{command}/{arg1}/{arg2}/...
    base, token = _upstash_cfg()
    if not base or not token:
        return None
    try:
        parts = [command] + [urllib.parse.quote(str(a), safe='') for a in args]
        url = base.rstrip('/') + '/' + '/'.join(parts)
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", "ignore")
            try:
                return json.loads(body)
            except Exception:
                return {"raw": body}
    except Exception:
        return None


def _append_mistake(obj: dict):
    # Try Upstash first
    payload = json.dumps(obj, ensure_ascii=False)
    res = _upstash_call("lpush", "mcq:m:mistakes", payload)
    if isinstance(res, dict) and ("result" in res or "error" not in res):
        return  # assume success if no explicit error
    # Fallback to local file (dev)
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        items = []
        if MISTAKES_PATH.exists():
            txt = MISTAKES_PATH.read_text(encoding="utf-8").strip()
            if txt:
                data = json.loads(txt)
                if isinstance(data, list):
                    items = data
        items.append(obj)
        MISTAKES_PATH.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        # Silently ignore in production to avoid 500s
        pass


def _upstash_scalar(command: str, args: list[str]):
    res = _upstash_call(command.lower(), *args)
    if isinstance(res, dict) and "result" in res:
        return res["result"]
    return None


def _mistakes_count() -> int:
    n = _upstash_scalar("LLEN", ["mcq:m:mistakes"])  # type: ignore[arg-type]
    if isinstance(n, int):
        return n
    # Fallback to file length in dev
    try:
        if MISTAKES_PATH.exists():
            data = json.loads(MISTAKES_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return len(data)
    except Exception:
        return 0
    return 0


def _load_mistakes_list() -> list:
    # Try Upstash first (newest first since we LPUSH)
    res = _upstash_call("lrange", "mcq:m:mistakes", "0", "-1")
    items: list = []
    if isinstance(res, dict) and isinstance(res.get("result"), list):
        arr = res["result"]
        for x in arr:
            try:
                items.append(json.loads(x) if isinstance(x, str) else x)
            except Exception:
                pass
    # Fallback to file (dev)
    if not items and MISTAKES_PATH.exists():
        try:
            data = json.loads(MISTAKES_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                items = data
        except Exception:
            items = []
    return items


@require_http_methods(["GET", "POST"])
def mcq(request):
    total = len(QUESTIONS)
    checked = {}
    score = 0
    streak = 0
    longest = 0

    if request.method == "POST":
        correctness = []
        for i, q in enumerate(QUESTIONS):
            key = f"q{i}"
            val = request.POST.get(key)
            try:
                selected_idx = int(val) if val is not None else None
            except (TypeError, ValueError):
                selected_idx = None
            is_correct = selected_idx is not None and selected_idx == q["answer"]
            correctness.append(is_correct)
            checked[key] = selected_idx
            if selected_idx is not None and not is_correct:
                try:
                    _append_mistake(q)
                except Exception:
                    pass
        score, streak, longest = _score_and_streak(correctness)

    # Prepare enriched question payloads including explanation and minimal attributes
    enriched = []
    for i, q in enumerate(QUESTIONS):
        # Defensive copies
        text = q.get("text", "")
        choices = q.get("choices", [])
        answer = q.get("answer", 0)
        explanation = q.get("explanation")
        # Minimal extras already computed during normalization
        extras = q.get("extras", {})
        enriched.append(
            {
                "index": i,
                "text": text,
                "choices": list(enumerate(choices)),
                "answer": answer,
                "selected": checked.get(f"q{i}"),
                "explanation": explanation,
                "extras": extras,
                # Provide only the data used client-side
                "json": json.dumps(
                    {
                        "choices": choices,
                        "answer": answer,
                        "explanation": explanation,
                    }
                ),
            }
        )

    context = {
        "questions": enriched,
        "total": total,
        "score": score,
        "streak": streak,
        "longest": longest,
        "checked": checked,
        "data_source": str(DATA_PATH),
    }
    return render(request, "quiz/mcq.html", context)


def reset(request):
    return redirect("mcq")


def home(request):
    # Build hierarchical grouping by top-level folder under data/
    # Example: Equity/Foo.json -> section "Equity" with item Foo.json
    groups = {}
    for p in sorted(DATA_DIR.rglob("*.json")):
        try:
            rel = p.relative_to(DATA_DIR)
        except ValueError:
            continue
        parts = list(rel.parts)
        if not parts:
            continue
        if len(parts) == 1:
            section = "General"
            fname = parts[0]
        else:
            section = parts[0]
            fname = str(rel)
        section_key = section
        groups.setdefault(section_key, [])
        groups[section_key].append(
            {
                "name": Path(fname).stem,
                "relpath": str(rel).replace("\\", "/"),
            }
        )
    # Sort groups and items within
    grouped = []
    for sec in sorted(groups.keys(), key=lambda s: s.lower()):
        items = sorted(groups[sec], key=lambda x: x["name"].lower())
        grouped.append({"section": sec, "items": items})
    mistakes_count = _mistakes_count()
    return render(request, "quiz/list.html", {"groups": grouped, "mistakes_count": mistakes_count})


def play(request, fname):
    # Render the MCQ page for the chosen JSON file within data/
    base = DATA_DIR.resolve()
    # Normalize and prevent path traversal
    target = (base / fname).resolve()
    if (
        not str(target).lower().endswith(".json")
        or not target.exists()
        or not target.is_file()
        or not target.is_relative_to(base)
    ):
        # Fallback to home listing if invalid
        return redirect("home")

    # Load and normalize questions from the selected file
    with target.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    questions = _normalize_questions(raw)

    total = len(questions)
    checked = {}
    score = 0
    streak = 0
    longest = 0

    if request.method == "POST":
        correctness = []
        for i, q in enumerate(questions):
            key = f"q{i}"
            val = request.POST.get(key)
            try:
                selected_idx = int(val) if val is not None else None
            except (TypeError, ValueError):
                selected_idx = None
            is_correct = selected_idx is not None and selected_idx == q["answer"]
            correctness.append(is_correct)
            checked[key] = selected_idx
            if selected_idx is not None and not is_correct:
                try:
                    _append_mistake(q)
                except Exception:
                    pass
        score, streak, longest = _score_and_streak(correctness)

    # Build enriched payload like legacy view
    enriched = []
    for i, q in enumerate(questions):
        text = q.get("text", q.get("stem", ""))
        choices = q.get("choices", [])
        answer = q.get("answer", 0)
        # Backward compatibility: support legacy shape with 'items' and 'correct' letter
        if (not choices) and isinstance(q.get("items"), list):
            try:
                items = q.get("items") or []
                choices = [v for _, v in items]
                correct = str(q.get("correct", "")).strip()
                letters = [k for k, _ in items]
                if correct in letters:
                    answer = letters.index(correct)
            except Exception:
                pass
        explanation = q.get("explanation")
        extras = q.get("extras", {})
        enriched.append(
            {
                "index": i,
                "text": text,
                "choices": list(enumerate(choices)),
                "answer": answer,
                "selected": checked.get(f"q{i}"),
                "explanation": explanation,
                "extras": extras,
                "json": json.dumps(
                    {
                        "choices": choices,
                        "answer": answer,
                        "explanation": explanation,
                    }
                ),
            }
        )

    context = {
        "questions": enriched,
        "total": total,
        "score": score,
        "streak": streak,
        "longest": longest,
        "checked": checked,
        "data_source": str(target),
    }
    return render(request, "quiz/mcq.html", context)


@require_http_methods(["GET", "POST"])
def master(request):
    # Aggregate questions from all JSON under data/, sample 180, and render
    all_questions = []
    files_used = []
    for p in sorted(DATA_DIR.rglob("*.json")):
        # Skip mistakes store
        if p.name.lower() == "mistakes.json":
            continue
        try:
            with p.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            qs = _normalize_questions(raw)
            if qs:
                all_questions.extend(qs)
                files_used.append(str(p.relative_to(DATA_DIR)).replace("\\", "/"))
        except Exception:
            continue

    if not all_questions:
        return redirect("home")

    sample_size = min(180, len(all_questions))
    # random.sample ensures unique indices and random order
    selection = random.sample(all_questions, sample_size)

    total = len(selection)
    checked = {}
    score = 0
    streak = 0
    longest = 0

    if request.method == "POST":
        correctness = []
        for i, q in enumerate(selection):
            key = f"q{i}"
            val = request.POST.get(key)
            try:
                selected_idx = int(val) if val is not None else None
            except (TypeError, ValueError):
                selected_idx = None
            is_correct = selected_idx is not None and selected_idx == q.get("answer", 0)
            correctness.append(is_correct)
            checked[key] = selected_idx
            if selected_idx is not None and not is_correct:
                try:
                    _append_mistake(q)
                except Exception:
                    pass
        score, streak, longest = _score_and_streak(correctness)

    enriched = []
    for i, q in enumerate(selection):
        text = q.get("text", "")
        choices = q.get("choices", [])
        answer = q.get("answer", 0)
        explanation = q.get("explanation")
        extras = q.get("extras", {})
        enriched.append(
            {
                "index": i,
                "text": text,
                "choices": list(enumerate(choices)),
                "answer": answer,
                "selected": checked.get(f"q{i}"),
                "explanation": explanation,
                "extras": extras,
                "json": json.dumps(
                    {
                        "choices": choices,
                        "answer": answer,
                        "explanation": explanation,
                        "extras": extras,
                    }
                ),
            }
        )

    context = {
        "questions": enriched,
        "total": total,
        "score": score,
        "streak": streak,
        "longest": longest,
        "checked": checked,
        "data_source": f"master: {total} from {len(files_used)} files",
    }
    return render(request, "quiz/mcq.html", context)


@require_http_methods(["GET", "POST"])
def mistakes(request):
    # Load mistakes as normalized questions
    questions = _load_mistakes_list()
    total = len(questions)
    checked = {}
    score = 0
    streak = 0
    longest = 0

    if request.method == "POST":
        correctness = []
        for i, q in enumerate(questions):
            key = f"q{i}"
            val = request.POST.get(key)
            try:
                selected_idx = int(val) if val is not None else None
            except (TypeError, ValueError):
                selected_idx = None
            is_correct = selected_idx is not None and selected_idx == q.get("answer", 0)
            correctness.append(is_correct)
            checked[key] = selected_idx
        score, streak, longest = _score_and_streak(correctness)

    enriched = []
    for i, q in enumerate(questions):
        text = q.get("text", "")
        choices = q.get("choices", [])
        answer = q.get("answer", 0)
        explanation = q.get("explanation")
        extras = q.get("extras", {})
        enriched.append(
            {
                "index": i,
                "text": text,
                "choices": list(enumerate(choices)),
                "answer": answer,
                "selected": checked.get(f"q{i}"),
                "explanation": explanation,
                "extras": extras,
                "json": json.dumps(
                    {
                        "choices": choices,
                        "answer": answer,
                        "explanation": explanation,
                    }
                ),
            }
        )

    context = {
        "questions": enriched,
        "total": total,
        "score": score,
        "streak": streak,
        "longest": longest,
        "checked": checked,
        "data_source": "mistakes",
    }
    return render(request, "quiz/mcq.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def api_mistake(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"ok": False, "error": "invalid payload"}, status=400)
    try:
        _append_mistake(payload)
    except Exception:
        pass
    return JsonResponse({"ok": True})
