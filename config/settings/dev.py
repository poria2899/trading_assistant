"""
Local development settings.

Run with: DJANGO_SETTINGS_MODULE=config.settings.dev (this is the default,
see manage.py / wsgi.py / asgi.py).
"""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# SQLite for development, per the project's tech stack decision.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Console backend so nothing is accidentally emailed during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
