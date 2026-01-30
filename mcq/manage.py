#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Also supports loading a simple .env file for local development so that
UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN can be provided
without exporting them in the shell every time.
"""
import os
import sys
from pathlib import Path


def _load_env_if_present():
    base = Path(__file__).resolve().parent
    candidates = [
        base / ".env.local",
        base / ".env",
        base.parent / ".env.local",
        base.parent / ".env",
    ]
    for p in candidates:
        try:
            if not p.exists() or not p.is_file():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # do not override existing environment
                if key and key not in os.environ:
                    os.environ[key] = val
        except Exception:
            # best-effort only
            pass


def main():
    """Run administrative tasks."""
    # Load local environment variables if available (dev convenience)
    _load_env_if_present()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcq.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
