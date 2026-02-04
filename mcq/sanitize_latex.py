from pathlib import Path
import re, json

MONEYISH_INLINE_DOLLAR = re.compile(
    r'(?<!\\)\$(?=[^$\n]*\s)(?=[^$\n]*[A-Za-z])(?![^$\n]*[+\-*/=^_\\])([^$\n]*)\$'
)

def sanitize(text: str) -> str:
    return MONEYISH_INLINE_DOLLAR.sub(r'USD \1', text)

def walk(x):
    if isinstance(x, str):
        return sanitize(x)
    if isinstance(x, list):
        return [walk(v) for v in x]
    if isinstance(x, dict):
        return {k: walk(v) for k, v in x.items()}
    return x

for p in Path("C:\\karma\\mcq\\mcq\\quiz\\data").rglob("*.json"):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        new = walk(data)
        if new != data:
            p.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("updated", p)
    except Exception as e:
        print("skip", p, "->", e)

