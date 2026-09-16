from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class StyledFormMixin:
    """Applies the Tailwind input/select classes to every field's widget.

    Presentation-only: it doesn't add, remove, or rename any field, it just
    sets the widget's `class` attribute so built-in Django forms render
    with the same design-system look as the rest of the app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            base_class = (
                "field-select" if isinstance(field.widget, forms.Select) else "field-input"
            )
            field.widget.attrs["class"] = (existing + " " + base_class).strip()


class RegisterForm(StyledFormMixin, UserCreationForm):
    """Registration form for the default Django User model.

    Built on Django's own UserCreationForm rather than a custom
    implementation. Adds an optional email field since that's commonly
    useful; everything else (username + password validation) is Django's
    built-in behavior.
    """

    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class StyledAuthenticationForm(StyledFormMixin, AuthenticationForm):
    """Django's built-in login form, with design-system widget classes."""
