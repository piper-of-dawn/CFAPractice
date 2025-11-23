
INSTALLED_APPS = [
    # ...
    "quiz",
]
# Use cookie-based sessions (avoid DB entirely)
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Templates & static (defaults are fine)
