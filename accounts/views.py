import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Customer


def _valid_phone(phone: str) -> bool:
    return bool(phone) and len(phone) == 10 and phone.isdigit() and phone[0] in "6789"


def _strong_password_error(password: str, user=None) -> str | None:
    """Return one message if the password is not strong enough."""
    missing = []
    if len(password) < 8:
        missing.append("at least 8 characters")
    if not re.search(r"[A-Z]", password):
        missing.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        missing.append("one lowercase letter")
    if not re.search(r"\d", password):
        missing.append("one number")
    if not re.search(r"[^A-Za-z0-9]", password):
        missing.append("one special character (such as ! @ # $)")
    if missing:
        return "Use a strong password with " + ", ".join(missing) + "."
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        return " ".join(exc.messages)
    return None


@require_http_methods(["GET", "POST"])
def register(request):
    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        ctx = {"next": next_url, "name": name, "phone": phone}

        if not name or len(name) < 2:
            messages.error(request, "Please enter your full name.")
            return render(request, "accounts/register.html", ctx)

        if not _valid_phone(phone):
            messages.error(request, "Enter a valid 10-digit mobile number starting with 6-9.")
            return render(request, "accounts/register.html", ctx)

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html", ctx)

        password_error = _strong_password_error(
            password, user=Customer(phone=phone, name=name)
        )
        if password_error:
            messages.error(request, password_error)
            return render(request, "accounts/register.html", ctx)

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "This number is already registered. Please login.")
            return redirect(f"{reverse('accounts:login')}?next={next_url}")

        user = Customer.objects.create_user(
            phone=phone,
            name=name,
            password=password,
            is_verified=True,
        )
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Welcome, {user.name}!")
        if next_url:
            return redirect(next_url)
        return redirect("properties:home")

    return render(request, "accounts/register.html", {"next": next_url})


@require_http_methods(["GET", "POST"])
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        ctx = {"next": next_url, "phone": phone}

        if not _valid_phone(phone):
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return render(request, "accounts/login.html", ctx)

        user = authenticate(request, username=phone, password=password)
        if user is None:
            if not Customer.objects.filter(phone=phone).exists():
                messages.error(request, "Number not found. Please register first.")
                return redirect(f"{reverse('accounts:register')}?next={next_url}")
            messages.error(request, "Wrong mobile number or password.")
            return render(request, "accounts/login.html", ctx)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Welcome, {user.name}!")
        if next_url:
            return redirect(next_url)
        return redirect("properties:home")

    return render(request, "accounts/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("properties:home")


def auth_choice(request):
    """Shown when user clicks I'm Interested without being logged in."""
    next_url = request.GET.get("next", "")
    return render(request, "accounts/auth_choice.html", {"next": next_url})
