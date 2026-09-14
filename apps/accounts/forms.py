from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """Registration form for the default Django User model.

    Built on Django's own UserCreationForm rather than a custom
    implementation. Adds an optional email field since that's commonly
    useful; everything else (username + password validation) is Django's
    built-in behavior.
    """

    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
