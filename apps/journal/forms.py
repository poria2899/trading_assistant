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

    def __init__(self, *args, **kwargs):
        """Attach the design-system input/select CSS classes.

        Presentation only — no field is added, removed, or renamed; this
        just sets each widget's `class` attribute so the form renders with
        the same look as the rest of the app.
        """
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.Textarea):
                base_class = "field-textarea"
            elif isinstance(field.widget, forms.Select):
                base_class = "field-select"
            else:
                base_class = "field-input"
            field.widget.attrs["class"] = (existing + " " + base_class).strip()

            if name == "risk_amount":
                field.widget.attrs.setdefault("placeholder", "0.00%")
                field.widget.attrs.setdefault("inputmode", "decimal")

            if name == "tags":
                field.widget.attrs.setdefault("placeholder", "e.g. breakout, news, revenge-trade")
            if name == "strategy":
                field.widget.attrs.setdefault("placeholder", "e.g. Breakout, Scalping")
            if name == "session":
                field.widget.attrs.setdefault("placeholder", "e.g. London, New York")
            if name == "asset":
                field.widget.attrs.setdefault("placeholder", "e.g. XAUUSD, EURUSD, BTCUSDT")

        self.fields["risk_amount"].label = "Risk Amount (%)"
