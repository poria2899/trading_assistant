"""
Root URL configuration for the Trade Assistant project.

Phase 1: admin, accounts (register/login/logout), core (home), and
placeholder journal/backtesting index pages are wired up. Future phases
will add real journal/backtesting/etc. URLs inside those apps' own
urls.py — this file stays a thin router.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("journal/", include("journal.urls")),
    path("backtesting/", include("backtesting.urls")),
]
