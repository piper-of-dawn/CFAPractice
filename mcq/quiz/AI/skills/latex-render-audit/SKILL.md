---
name: latex-render-audit
description: Detect and fix CFA quiz JSON question objects whose currency dollar signs or malformed math delimiters break LaTeX rendering. Use when rendered questions show glued prose, giant italic text, or normal currency amounts being interpreted as math.
---

# LaTeX Render Audit

Use this skill before or after editing quiz JSON when `$` rendering looks wrong.

## Goal

Find question objects where plain currency such as `$8 million` was written with a dollar sign and is being treated as a math delimiter. Currency must be written as `USD 8 million`, `EUR 30`, etc. Real math may use `$...$`, but malformed or odd dollar delimiters should be flagged before changing data.

## Quick Workflow

1. Run the detector against the quiz data root:

```bash
python AI/skills/latex-render-audit/scripts/detect_latex_render_issues.py mcq/quiz/data
```

2. Review each reported object by `file`, `index`, `id`, `topic`, and `field`.

3. Apply only narrow fixes:

```bash
python AI/skills/latex-render-audit/scripts/detect_latex_render_issues.py mcq/quiz/data --fix-currency
```

4. Validate JSON after any write:

```bash
python AI/skills/latex-render-audit/scripts/detect_latex_render_issues.py mcq/quiz/data --validate-only
```

## What To Flag

- `currency_dollar`: unescaped `$` before an amount in prose, for example `$8 million`.
- `odd_dollar_count`: a string has an odd number of unescaped `$` delimiters.
- `prose_math_span`: text between `$...$` contains likely prose, HTML, or long joined words rather than math.

## Fixing Rules

- Convert currency dollar signs to ISO-style text, for example `$8 million` -> `USD 8 million`.
- Do not convert formulas such as `$PV = FV/(1+r)^t$`.
- If a string has odd dollar delimiters, inspect manually. Do not blindly alternate delimiters.
- If explanations contain generated draft notes such as "Wait", "Let's recalculate", or "Corrected", treat that as a content quality issue separate from LaTeX rendering.

## Safety

The bundled script defaults to detection only. `--fix-currency` rewrites only currency-like dollar signs in valid JSON files and revalidates every touched file.
