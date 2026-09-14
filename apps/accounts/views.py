from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    """Create a normal Django User and log them in immediately.

    Login/logout themselves use Django's built-in LoginView/LogoutView
    (wired directly in urls.py) rather than custom views, since the
    built-ins already do exactly what Phase 1 needs.
    """
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
