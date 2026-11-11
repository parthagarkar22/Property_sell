from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def broker_required(view_func):
    """Only staff/superuser (broker) can open the dashboard."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dashboard:login")
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "This area is only for the broker.")
            return redirect("properties:home")
        return view_func(request, *args, **kwargs)

    return _wrapped
