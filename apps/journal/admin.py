from django.contrib import admin

from .models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """Minimal admin registration for verifying Trade data during
    development. No custom journal UI is built here — that's Phase 2.2+.
    """

    list_display = ("date", "time", "asset", "direction", "timeframe", "result", "user")
    list_filter = ("direction", "timeframe", "result")
    search_fields = ("asset", "strategy", "tags", "notes")
