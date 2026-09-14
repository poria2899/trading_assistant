"""
Base settings shared by all environments.

Environment-specific overrides live in dev.py and prod.py.
Do not put environment-specific values (DEBUG, ALLOWED_HOSTS, DB creds) here.
"""

import os
import sys
from pathlib import Path

# BASE_DIR = the trade_assistant/ project root (three levels up from this
# file: config/settings/base.py -> config/settings -> config -> BASE_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Make the "apps" package importable as top-level modules (e.g. "journal"
# instead of "apps.journal"), which keeps INSTALLED_APPS entries short and
# avoids deep import paths throughout the codebase.
sys.path.insert(0, str(BASE_DIR / "apps"))


def env(key, default=None):
    """Tiny helper to read environment variables with a default.

    A real .env loader (e.g. python-dotenv) can replace this later if
    needed. Kept dependency-free for now since Phase 0 doesn't need more
    than plain environment variable lookups.
    """
    return os.environ.get(key, default)


# SECURITY WARNING: keep the secret key used in production secret!
# The default below is ONLY for local development convenience and is
# intentionally obvious/insecure. Production MUST set DJANGO_SECRET_KEY.
SECRET_KEY = env("DJANGO_SECRET_KEY", "django-insecure-dev-key-do-not-use-in-production")

# DEBUG, ALLOWED_HOSTS, and DATABASES are intentionally NOT set here.
# They differ per environment and are defined in dev.py / prod.py.

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps (Phase 0: scaffolding only, no models/views yet)
    "core",
    "accounts",
    "journal",
    "backtesting",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates (shared base.html, layout, etc.) live in
        # /templates. Each app can still keep its own templates/<app>/ dir
        # via APP_DIRS for app-specific pages.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# Project-level static assets (shared css/js) live in /static during
# development. STATIC_ROOT (collectstatic target) is defined per-environment
# since it's typically only used in production.
STATICFILES_DIRS = [BASE_DIR / "static"]

# User-uploaded content (trade screenshots, etc. in later phases).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "accounts:login"
