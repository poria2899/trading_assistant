from django.conf import settings
from django.db import models


class Direction(models.TextChoices):
    BUY = "BUY", "Buy"
    SELL = "SELL", "Sell"


class Timeframe(models.TextChoices):
    M1 = "M1", "M1"
    M5 = "M5", "M5"
    M15 = "M15", "M15"
    M30 = "M30", "M30"
    H1 = "H1", "H1"
    H4 = "H4", "H4"
    D1 = "D1", "D1"


class Result(models.TextChoices):
    WIN = "WIN", "Win"
    LOSS = "LOSS", "Loss"
    RISK_FREE = "RISK_FREE", "Risk Free"


class Trade(models.Model):
    """One real/actual trade recorded in a user's trading journal.

    Phase 2.1 scope: raw data storage only. No calculated fields (P/L,
    R multiple, risk/reward, duration, statistics) — those are derived
    later from the raw prices/sizes stored here.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journal_trades",
        help_text="The user this trade belongs to. Trades are private to their owner.",
    )

    date = models.DateField()
    time = models.TimeField()

    asset = models.CharField(
        max_length=20,
        help_text="e.g. XAUUSD, EURUSD, BTCUSDT",
    )
    direction = models.CharField(max_length=4, choices=Direction.choices)
    timeframe = models.CharField(max_length=3, choices=Timeframe.choices)

    # Financial values use DecimalField (never float) for exactness.
    # max_digits/decimal_places are generous enough to cover forex lot
    # sizes (e.g. 0.01 lots) up to crypto/index prices with several
    # decimal places, without being needlessly oversized.
    position_size = models.DecimalField(max_digits=12, decimal_places=4)
    entry_price = models.DecimalField(max_digits=14, decimal_places=5)
    stop_loss = models.DecimalField(max_digits=14, decimal_places=5, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=14, decimal_places=5, null=True, blank=True)
    exit_price = models.DecimalField(max_digits=14, decimal_places=5, null=True, blank=True)
    risk_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    strategy = models.CharField(max_length=100, blank=True)
    session = models.CharField(max_length=50, blank=True)

    result = models.CharField(max_length=10, choices=Result.choices, default=Result.WIN)

    notes = models.TextField(blank=True)
    # Simple comma-separated tags for now — no dedicated tagging system.
    # e.g. "breakout, news, revenge-trade"
    tags = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-time"]
        indexes = [
            # The journal's primary access pattern is "this user's trades,
            # most recent first" — index the fields that filter/order
            # every query rather than adding speculative indexes.
            models.Index(fields=["user", "-date"]),
        ]

    def __str__(self):
        return f"{self.asset} {self.direction} {self.date} ({self.get_result_display()})"
