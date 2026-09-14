from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """Placeholder — Backtesting itself is built starting Phase 5."""
    return render(request, "backtesting/index.html")
