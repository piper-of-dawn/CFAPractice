import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

# Reuse helpers and normalization from views
from quiz.views import (
    DATA_DIR,
    _normalize_questions,
    _upstash_call,
    _upstash_cfg,
)


def _iter_all_questions():
    """Yield normalized questions from every JSON under data/, with a derived topic.

    Topic is taken from extras['topic'] if present, else from the top-level folder name.
    """
    base = DATA_DIR.resolve()
    for p in sorted(base.rglob("*.json")):
        if p.name.lower() == "mistakes.json":
            continue
        try:
            with p.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            qs = _normalize_questions(raw)
        except Exception:
            continue
        # Derive topic from path if not present
        try:
            rel = p.relative_to(base)
            parts = list(rel.parts)
            topic_from_path = parts[0] if len(parts) > 1 else "General"
        except Exception:
            topic_from_path = "General"
        for q in qs:
            extras = dict(q.get("extras") or {})
            if not extras.get("topic"):
                extras["topic"] = extras.get("category") or topic_from_path
            yield {
                "text": q.get("text") or "",
                "choices": list(q.get("choices") or []),
                "answer": int(q.get("answer") or 0),
                "explanation": q.get("explanation"),
                "extras": extras,
            }


def _signature(choices, answer):
    # Build a robust signature using normalized choices and answer index
    norm_choices = tuple((c or "").strip() for c in (choices or []))
    try:
        a = int(answer)
    except Exception:
        a = 0
    return (norm_choices, a)


class Command(BaseCommand):
    help = "Backfill Upstash mistakes with missing text and topic by matching local question bank"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply updates (default is dry-run)",
        )
        parser.add_argument(
            "--key",
            default="mcq:m:mistakes",
            help="Upstash list key to backfill (default: mcq:m:mistakes)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional max items to process (0 = all)",
        )

    def handle(self, *args, **opts):
        base, token = _upstash_cfg()
        if not base or not token:
            raise CommandError("UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set")

        key = opts["key"]
        do_apply = opts["apply"]
        limit = opts["limit"] or -1

        # Build lookup from local question bank
        lookup = {}
        for q in _iter_all_questions():
            sig = _signature(q.get("choices"), q.get("answer"))
            lookup.setdefault(sig, []).append(q)

        # Fetch full list from Upstash
        res = _upstash_call("lrange", key, "0", "-1")
        if not (isinstance(res, dict) and isinstance(res.get("result"), list)):
            raise CommandError("Failed to LRANGE from Upstash; check credentials and key")
        arr = res["result"]
        n = len(arr)

        updated = 0
        examined = 0
        for idx, raw in enumerate(arr):
            if limit >= 0 and examined >= limit:
                break
            examined += 1
            try:
                item = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                continue
            if not isinstance(item, dict):
                continue

            changed = False
            choices = item.get("choices") or []
            answer = item.get("answer") or 0
            sig = _signature(choices, answer)
            match_list = lookup.get(sig) or []
            match = match_list[0] if match_list else None

            # Fill missing text
            text = (item.get("text") or "").strip()
            if (not text) and match and match.get("text"):
                item["text"] = match["text"]
                changed = True

            # Ensure extras.topic
            extras = item.get("extras") or {}
            if not isinstance(extras, dict):
                extras = {}
            topic = (extras.get("topic") or "").strip()
            if (not topic) and match:
                mt = match.get("extras", {}).get("topic")
                if mt:
                    extras["topic"] = mt
                    item["extras"] = extras
                    changed = True

            if changed and do_apply:
                # Write back in-place at the same index
                payload = json.dumps(item, ensure_ascii=False)
                _ = _upstash_call("lset", key, str(idx), payload)
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfill complete: examined={examined}, updated={updated}, total_in_list={n}, apply={do_apply}"
            )
        )

