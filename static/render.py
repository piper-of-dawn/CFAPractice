
# -*- coding: utf-8 -*-
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import random
ROOT = Path(__file__).parent
COMP = ROOT / "components"

TEMPLATE_FILE = COMP / "template.txt"
CSS_FILE = COMP / "style.css"
OUTCOME_FILE = COMP / "outcome.html"
APP_JS_FILE = COMP / "app.js"


def _read(p: Path, default: str = "") -> str:
    return p.read_text(encoding="utf-8") if p.exists() else default


def _normalize_questions(raw):
    """Accept list or {'questions':[...]} and normalize to a uniform structure."""
    data = raw
    norm = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for q in data:
        opts = q.get("options", [])
        correct = q.get("correct_answer", q.get("answer", ""))

        if isinstance(opts, dict):
            # Keep labeled choices; preserve A,B,C order if possible
            items = [(k, opts[k]) for k in sorted(opts.keys(), key=lambda x: str(x))]
            # If correct is numeric by mistake, map it to a letter order
            if isinstance(correct, int):
                if 0 <= correct < len(items):
                    correct = items[correct][0]
                else:
                    correct = ""
        else:
            # List -> assign letters
            items = [(letters[i], v) for i, v in enumerate(opts)]
            # Map numeric correct index -> letter
            if isinstance(correct, int):
                if 0 <= correct < len(items):
                    correct = items[correct][0]
                else:
                    correct = ""

        norm.append({
            "id": q.get("id", ""),
            "model": q.get("model", ""),
            "topic": q.get("topic", ""),
            "difficulty": q.get("difficulty", ""),
            "stem": q.get("stem", q.get("text", "")),
            "items": items,             # list of (letter, text)
            "correct": str(correct).strip(),  # letter like 'A'
            "explanation": q.get("explanation", ""),
        })
        item = norm.pop()
        idx = random.randint(0, len(norm))
        norm.insert(idx, item)
    return norm


# Use bracket lookup to avoid colliding with dict.items() method
QUESTIONS_SNIPPET = Template("""
{% for q in questions %}
<article class="card" data-qid="{{ q.id }}" data-correct="{{ q.correct }}" data-expl="{{ q.explanation|e }}">
  <h2>{{ loop.index }}. {{ q.stem }}</h2>
  <form class="q">
    {% for letter, text in q["items"] %}
    <label class="option">
      <input type="radio" name="{{ q.id }}" value="{{ letter }}">
      <span><strong>{{ letter }}.</strong> {{ text }}</span>
    </label>
    {% endfor %}
  </form>

  <div class="q-footer">
    <div class="subtle">
      {% if q.topic %}Topic: {{ q.topic }}{% endif %}
      {% if q.model %}{% if q.topic %} | {% endif %}Model: {{ q.model }}{% endif %}
    </div>
    <button class="btn btn-primary btn-check" type="button">Check</button>
  </div>
</article>
{% endfor %}
""".strip())

DEFAULT_OUTCOME = """
<div class="result-card pending">
  <h3 data-role="status">PENDING</h3>
  <div class="stats">
    <div class="stat"><div class="val" data-role="accuracy">0%</div><div>Accuracy</div></div>
    <div class="stat"><div class="val" data-role="answered">0</div><div>Answered</div></div>
    <div class="stat"><div class="val" data-role="current">0</div><div>Current Streak</div></div>
    <div class="stat"><div class="val" data-role="best">0</div><div>Best Streak</div></div>
  </div>
</div>
""".strip()

DEFAULT_EXPLANATION = """
<div class="explanation">
  <h3>Explanation</h3>
  <p>Select an answer to see feedback here.</p>
</div>
""".strip()


def render(json_path: Path, template_path: Path = TEMPLATE_FILE, out_path: Path = ROOT / "index.html"):
    raw = json.loads(Path(json_path).read_text(encoding="utf-8"))
    questions = _normalize_questions(raw)

    css = _read(CSS_FILE)
    outcome_html = _read(OUTCOME_FILE, DEFAULT_OUTCOME)
    explanation_html = DEFAULT_EXPLANATION
    questions_html = QUESTIONS_SNIPPET.render(questions=questions)

    env = Environment(
        loader=FileSystemLoader([str(template_path.parent), str(COMP)]),
        autoescape=select_autoescape(["html"])
    )
    tpl = env.get_template(template_path.name)
    html = tpl.render(css=css, questions=questions_html,
                      outcome=outcome_html, explanation=explanation_html)

    if APP_JS_FILE.exists():
        html = html.replace("</body>", '<script src="components/app.js"></script>\n</body>')

    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path} with {len(questions)} questions.")


def main():
    import sys
    import random
    if len(sys.argv) < 2:
        print("Usage: python render.py <questions.json> [template.html] [out.html]")
        raise SystemExit(1)
    json_path = Path(sys.argv[1])
    template_path = Path(sys.argv[2]) if len(sys.argv) > 2 else TEMPLATE_FILE
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "index.html"
    render(json_path, template_path, out_path)


if __name__ == "__main__":
    main()
