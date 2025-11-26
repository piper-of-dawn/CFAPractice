import os
import sys
from pathlib import Path

# Configure Django settings for the serverless function
ROOT = Path(__file__).resolve().parents[1]
OUTER_DJANGO_DIR = ROOT / "mcq"

# Ensure both repo root (for top-level apps) and Django outer dir are importable
for p in (str(ROOT), str(OUTER_DJANGO_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcq.settings")

from django.core.asgi import get_asgi_application

# Expose ASGI app for Vercel Python runtime
app = get_asgi_application()
