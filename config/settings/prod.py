"""
Production settings scaffold.

Not wired up or exercised yet (Phase 0 only targets local development).
This exists so the eventual move to PostgreSQL + a real deployment doesn't
require restructuring settings, only filling in these values via
environment variables.
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", "").split(",") if env("DJANGO_ALLOWED_HOSTS") else []

# PostgreSQL, driven entirely by environment variables. psycopg is not
# installed yet — add it to requirements.txt when this settings module is
# actually put into use.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST", "localhost"),
        "PORT": env("DATABASE_PORT", "5432"),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
