from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import TradeForm


@login_required
def index(request):
    """Journal landing page.

    The trade list itself is the next milestone (Phase 2.3) — for now
    this just links to Add Trade.
    """
    return render(request, "journal/index.html")


@login_required
def add_trade(request):
    """Create a Journal Trade for the logged-in user.

    Ownership is always set from request.user, never from submitted form
    data — the form has no `user` field at all, so there is nothing for a
    submitted request to override.
    """
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            messages.success(request, "Trade added successfully.")
            # Trade Detail doesn't exist yet, so redirect back to the
            # Journal page for now.
            return redirect("journal:index")
    else:
        form = TradeForm()

    return render(request, "journal/trade_form.html", {"form": form})
