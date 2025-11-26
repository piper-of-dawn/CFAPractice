from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from pathlib import Path
import json


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
    if "â" in val or "�" in val:
        try:
            fixed = val.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
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
                if letter in choices and False:  # placeholder to keep branch structure readable
                    pass
        elif isinstance(q.get("options"), dict) and q.get("options"):
            opts = q["options"]
            # Keep alphabetical A..Z ordering for stable UI
            letters = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c in opts]
            choices = [_fix_mojibake(opts[k]) for k in letters]
            # Derive answer index from a letter-like field
            ans_letter = (q.get("correct_answer") or q.get("answer_letter") or "").strip().upper()
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
        explanation = _fix_mojibake(q.get("explanation") or q.get("explanations") or q.get("rationale"))

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
                "json": json.dumps({
                    "choices": choices,
                    "answer": answer,
                    "explanation": explanation,
                }),
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
    # List all available JSON files under data/ (including subfolders)
    files = []
    for p in sorted(DATA_DIR.rglob("*.json")):
        try:
            rel = p.relative_to(DATA_DIR)
        except ValueError:
            # Shouldn't happen, but skip anything outside
            continue
        files.append({
            "name": rel.stem,
            "relpath": str(rel).replace("\\", "/"),
        })
    return render(request, "quiz/list.html", {"files": files})


def play(request, fname):
    # Render the MCQ page for the chosen JSON file within data/
    base = DATA_DIR.resolve()
    # Normalize and prevent path traversal
    target = (base / fname).resolve()
    if not str(target).lower().endswith('.json') or not target.exists() or not target.is_file() or not target.is_relative_to(base):
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
        score, streak, longest = _score_and_streak(correctness)

    # Build enriched payload like legacy view
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
                "json": json.dumps({
                    "choices": choices,
                    "answer": answer,
                    "explanation": explanation,
                }),
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
