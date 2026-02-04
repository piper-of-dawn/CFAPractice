# test_sanitize_dollars.py
# Run: pytest -q

import re
import pytest

# Heuristic: replace $...$ with "USD ..." ONLY when the inside looks like prose money,
# not real math: has whitespace + letters, and has NO obvious math operators and NO backslash commands.
MONEYISH_INLINE_DOLLAR = re.compile(
    r'(?<!\\)\$(?=[^$\n]*\s)(?=[^$\n]*[A-Za-z])(?![^$\n]*[+\-*/=^_\\])([^$\n]*)\$'
)

def sanitize(text: str) -> str:
    return MONEYISH_INLINE_DOLLAR.sub(r'USD \1', text)

@pytest.mark.parametrize(
    "inp, out",
    [
        # --- should NOT change: valid LaTeX math ---
        (r"$1 + 1 = 2$", r"$1 + 1 = 2$"),
        (r"$x$", r"$x$"),
        (r"$r_t$", r"$r_t$"),
        (r"$x^2$", r"$x^2$"),
        (r"$x_1$", r"$x_1$"),
        (r"$a/b$", r"$a/b$"),
        (r"$\alpha$", r"$\alpha$"),
        (r"$\frac{1}{2}$", r"$\frac{1}{2}$"),
        (r"$100 \text{ million}$", r"$100 \text{ million}$"),
        (r"$\text{USD }100$", r"$\text{USD }100$"),

        # --- should change: prose-money mistakenly wrapped in $...$ ---
        (r"$100 million$", r"USD 100 million"),
        (r"$1 billion$", r"USD 1 billion"),
        (r"$115 mn$", r"USD 115 mn"),
        (r"Cost is $100 million$ today.", r"Cost is USD 100 million today."),
        (r"($100 million$) and ($1 billion$).", r"(USD 100 million) and (USD 1 billion)."),

        # --- should NOT change: no whitespace or no letters (ambiguous) ---
        (r"$100$", r"$100$"),                 # no letters => leave (could be math)
        (r"$100million$", r"$100million$"),   # no whitespace => leave
        (r"$abc$", r"$abc$"),                 # letters but no whitespace => leave (could be variable)

        # --- should NOT change: contains math/operator/backslash (treat as real math) ---
        (r"$100 million + 2$", r"$100 million + 2$"),
        (r"$profit = 100 million$", r"$profit = 100 million$"),
        (r"$x \times y$", r"$x \times y$"),

        # --- escaped dollars should be untouched ---
        (r"\$100 million$", r"\$100 million$"),
        (r"Price: \$100 million$ (typo)", r"Price: \$100 million$ (typo)"),
    ],
)
def test_sanitize_cases(inp, out):
    assert sanitize(inp) == out

def test_multiple_matches_in_one_line():
    s = r"Deal: $100 million$ then $1 billion$."
    assert sanitize(s) == r"Deal: USD 100 million then USD 1 billion."

def test_idempotent():
    s = r"Deal: $100 million$ and math $1 + 1 = 2$."
    once = sanitize(s)
    twice = sanitize(once)
    assert once == twice

def test_does_not_cross_newlines():
    s = "$100 million\n$1 + 1 = 2$"
    # first token is unterminated on that line -> no match; second is valid math -> no change
    assert sanitize(s) == s
