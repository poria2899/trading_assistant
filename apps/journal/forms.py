from django import forms

from .models import Trade


class TradeForm(forms.ModelForm):
    """Add/edit form for a Journal Trade.

    Deliberately excludes `user`, `created_at`, and `updated_at` — the
    owner is always set from request.user in the view, never from
    submitted form data, and the timestamps are automatic.
    """

    class Meta:
        model = Trade
        fields = [
            "date",
            "time",
            "asset",
            "direction",
            "timeframe",
            "position_size",
            "entry_price",
            "stop_loss",
            "take_profit",
            "exit_price",
            "strategy",
            "session",
            "risk_amount",
            "result",
            "notes",
            "tags",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
