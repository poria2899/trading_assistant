from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """Placeholder — the Trading Journal itself is built in Phase 2."""
    return render(request, "journal/index.html")
