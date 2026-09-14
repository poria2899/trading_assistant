from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    """Authenticated home/dashboard placeholder.

    Foundation-level only: welcome message, username, links to the other
    sections. No trading statistics/analytics here — those start in later
    phases once there's actual data to summarize.
    """
    return render(request, "core/home.html")
