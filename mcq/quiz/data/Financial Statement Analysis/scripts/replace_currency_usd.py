#!/usr/bin/env python3
import sys
import os
import re


def transform(text: str) -> str:
    # Pre-fix: revert prior mistaken replacements like 'USD32 ... $' back to math start '$'
    text = re.sub(r'USD(?=\s*\d[^$]*\$)', '$', text)

    # Mask display math $$...$$
    disp_pat = re.compile(r"\$\$.*?\$\$", re.DOTALL)
    disp_segments = []

    def _mask_disp(m):
        idx = len(disp_segments)
        disp_segments.append(m.group(0))
        return f"__DISP_MATH_{idx}__"

    text = disp_pat.sub(_mask_disp, text)

    # Mask inline math $...$ that does NOT start with a currency-like pattern
    inline_pat = re.compile(r"\$(?!\s*[\d(]).*?\$", re.DOTALL)
    inline_segments = []

    def _mask_inline(m):
        idx = len(inline_segments)
        inline_segments.append(m.group(0))
        return f"__INLINE_MATH_{idx}__"

    text = inline_pat.sub(_mask_inline, text)

    # Currency replacements: 'US$' -> 'USD', then standalone '$' before digits/paren -> 'USD'
    text = re.sub(r"US\$(?=\s*[\d(])", "USD", text)
    text = re.sub(r"\$(?=\s*[\d(])", "USD", text)

    # Unmask math segments
    for idx, seg in enumerate(inline_segments):
        text = text.replace(f"__INLINE_MATH_{idx}__", seg)
    for idx, seg in enumerate(disp_segments):
        text = text.replace(f"__DISP_MATH_{idx}__", seg)

    return text


def process_file(path: str) -> int:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    transformed = transform(original)
    if transformed != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(transformed)
        return 1
    return 0


def main(root: str) -> int:
    changed = 0
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith('.json'):
                path = os.path.join(dirpath, fn)
                changed += process_file(path)
    print(f"Files updated: {changed}")
    return 0


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    raise SystemExit(main(root))
