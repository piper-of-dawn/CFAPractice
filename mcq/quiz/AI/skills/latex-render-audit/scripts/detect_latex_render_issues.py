#!/usr/bin/env python3
"""Detect quiz JSON strings likely to break dollar-delimited LaTeX rendering."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


CURRENCY_DOLLAR_RE = re.compile(
    r"(?<!\\)\$([0-9][0-9,]*(?:\.[0-9]+)?)"
    r"(?=\s*(?:"
    r"million|billion|thousand|dollars?\b|M\b|m\b|B\b|bn\b|"
    r"par\b|face\b|principal\b|coupon\b|cash\b|price\b|value\b|"
    r"salvage\b|proceeds\b|payment\b|payments\b|revenue\b|cost\b|costing\b|"
    r"investment\b|invested\b|committed\b|loan\b|debt\b|equity\b|"
    r"asset\b|assets\b|fund\b|funds\b|profit\b|loss\b|"
    r"dividend\b|dividends\b|shares?\b|inventory\b|accounts?\b|COGS\b|CFO\b"
    r"))"
)

UNESCAPED_DOLLAR_RE = re.compile(r"(?<!\\)\$")
WORD_RE = re.compile(r"[A-Za-z]{4,}")
HTML_RE = re.compile(r"</?[A-Za-z][^>]*>")

MATH_WORD_ALLOWLIST = {
    "text",
    "frac",
    "times",
    "left",
    "right",
    "mathrm",
    "Delta",
    "Yield",
    "Full",
    "Duration",
    "Macaulay",
    "Investment",
    "horizon",
    "Weight",
    "Present",
    "value",
    "cash",
    "flow",
    "Bond",
    "coupon",
    "receipt",
    "Price",
    "AnnConvexity",
    "MoneyCon",
    "MoneyDur",
    "ModDur",
    "MacDur",
    "ApproxCon",
    "Curve",
    "PV",
    "FV",
    "PMT",
    "USD",
    "EUR",
    "GBP",
    "CAD",
    "INR",
    "Days",
    "Year",
    "days",
    "year",
    "years",
    "bps",
}


@dataclass
class Issue:
    file: Path
    object_path: str
    question_id: Any
    topic: str
    field: str
    kind: str
    excerpt: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "file": str(self.file),
            "object_path": self.object_path,
            "id": self.question_id,
            "topic": self.topic,
            "field": self.field,
            "kind": self.kind,
            "excerpt": self.excerpt,
        }


def iter_json_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix == ".json":
            yield path
        elif path.is_dir():
            yield from sorted(path.rglob("*.json"))


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(json.dumps({"file": str(path), "kind": "invalid_json", "error": str(exc)}))
        return None


def preview(text: str, start: int = 0, end: int | None = None) -> str:
    if end is None:
        end = min(len(text), start + 180)
    left = max(0, start - 60)
    right = min(len(text), end + 80)
    return text[left:right].replace("\n", " | ")


def dollar_spans(text: str) -> list[tuple[int, int, str]]:
    matches = list(UNESCAPED_DOLLAR_RE.finditer(text))
    spans: list[tuple[int, int, str]] = []
    for left, right in zip(matches[0::2], matches[1::2]):
        spans.append((left.start(), right.end(), text[left.end() : right.start()]))
    return spans


def find_string_issues(
    file: Path,
    object_path: str,
    question_id: Any,
    topic: str,
    field: str,
    value: str,
) -> list[Issue]:
    issues: list[Issue] = []

    for match in CURRENCY_DOLLAR_RE.finditer(value):
        issues.append(
            Issue(file, object_path, question_id, topic, field, "currency_dollar", preview(value, match.start(), match.end()))
        )

    dollar_count = len(UNESCAPED_DOLLAR_RE.findall(value))
    if dollar_count % 2:
        issues.append(Issue(file, object_path, question_id, topic, field, "odd_dollar_count", preview(value)))

    for start, end, span in dollar_spans(value):
        words = [word for word in WORD_RE.findall(span) if word not in MATH_WORD_ALLOWLIST]
        has_long_word = any(len(word) >= 16 for word in words)
        has_html = bool(HTML_RE.search(span))
        if has_html or has_long_word or len(words) >= 5:
            issues.append(Issue(file, object_path, question_id, topic, field, "prose_math_span", preview(value, start, end)))

    return issues


def walk_strings(value: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_strings(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            yield from walk_strings(child, child_prefix)


def question_objects(data: Any) -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, dict):
                yield f"[{index}]", item
    elif isinstance(data, dict):
        questions = data.get("questions")
        if isinstance(questions, list):
            for index, item in enumerate(questions):
                if isinstance(item, dict):
                    yield f".questions[{index}]", item


def detect_file(path: Path) -> list[Issue]:
    data = load_json(path)
    if data is None:
        return []

    issues: list[Issue] = []
    objects = list(question_objects(data))
    if objects:
        for object_path, obj in objects:
            question_id = obj.get("id")
            topic = str(obj.get("topic", ""))
            for field, value in walk_strings(obj):
                issues.extend(find_string_issues(path, object_path, question_id, topic, field, value))
    else:
        for field, value in walk_strings(data):
            issues.extend(find_string_issues(path, "", None, "", field, value))
    return issues


def fix_currency_file(path: Path) -> int:
    original = path.read_text()
    if load_json(path) is None:
        return 0
    updated, count = CURRENCY_DOLLAR_RE.subn(r"USD \1", original)
    if count == 0:
        return 0
    json.loads(updated)
    path.write_text(updated)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="JSON file or directory paths to scan.")
    parser.add_argument("--fix-currency", action="store_true", help="Rewrite currency-like $ amounts to USD amounts.")
    parser.add_argument("--validate-only", action="store_true", help="Only validate JSON parseability.")
    args = parser.parse_args()

    files = list(iter_json_files(args.paths))
    if args.validate_only:
        bad = 0
        for path in files:
            if load_json(path) is None:
                bad += 1
        print(json.dumps({"json_files": len(files), "invalid_json": bad}))
        return 1 if bad else 0

    if args.fix_currency:
        total = 0
        touched = 0
        for path in files:
            count = fix_currency_file(path)
            if count:
                touched += 1
                total += count
                print(json.dumps({"file": str(path), "currency_replacements": count}))
        print(json.dumps({"changed_files": touched, "currency_replacements": total}))

    issues: list[Issue] = []
    for path in files:
        issues.extend(detect_file(path))

    for issue in issues:
        print(json.dumps(issue.as_dict(), ensure_ascii=False))

    print(json.dumps({"json_files": len(files), "issues": len(issues)}))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
