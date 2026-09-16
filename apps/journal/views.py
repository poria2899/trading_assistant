from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TradeForm
from .models import Trade


@login_required
def index(request):
    """Journal landing page: the current user's trade list.

    Ownership is enforced in the query itself (filter(user=request.user))
    so this view can never return another user's trades. Ordering relies
    on the Trade model's default ordering (-date, -time).
    """
    trades = Trade.objects.filter(user=request.user)
    return render(request, "journal/index.html", {"trades": trades})


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


@login_required
def trade_detail(request, pk):
    """Show one trade's full detail.

    Ownership is enforced directly in the query — the authenticated user
    is part of the lookup, not checked afterward — so a trade belonging
    to another user 404s exactly like a non-existent trade does. This
    deliberately doesn't reveal whether the trade exists at all.
    """
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    return render(request, "journal/trade_detail.html", {"trade": trade})
