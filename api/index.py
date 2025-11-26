import os
import sys
from pathlib import Path

# Configure Django settings for the serverless function
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcq.settings")

from django.core.asgi import get_asgi_application

# Expose ASGI app for Vercel Python runtime
app = get_asgi_application()
