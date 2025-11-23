from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from pathlib import Path
import json


def load_questions():
    # Load from the requested module file (with spaces and colon in name)
    data_path = (
        Path(__file__).resolve().parent
        / "data"
        / "Module 6: Fixed-Income Bond Valuation: Prices and Yields.json"
    )
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


QUESTIONS = load_questions()


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

    # Prepare enriched question payloads including explanation and arbitrary attributes
    enriched = []
    for i, q in enumerate(QUESTIONS):
        # Defensive copies
        text = q.get("text", "")
        choices = q.get("choices", [])
        answer = q.get("answer", 0)
        explanation = q.get("explanation") or q.get("explanations")
        # Collect extra attributes excluding core ones
        extras = {k: v for k, v in q.items() if k not in {"text", "choices", "answer", "explanation", "explanations"}}
        enriched.append(
            {
                "index": i,
                "text": text,
                "choices": list(enumerate(choices)),
                "answer": answer,
                "selected": checked.get(f"q{i}"),
                "explanation": explanation,
                "extras": extras,
                "json": json.dumps(q),
            }
        )

    context = {
        "questions": enriched,
        "total": total,
        "score": score,
        "streak": streak,
        "longest": longest,
        "checked": checked,
        "data_source": str(
            Path(__file__).resolve().parent
            / "data"
            / "Module 6: Fixed-Income Bond Valuation: Prices and Yields.json"
        ),
    }
    return render(request, "quiz/mcq.html", context)


def reset(request):
    return redirect("mcq")
