from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import Interest, Property
from .notify import interest_whatsapp_url, notify_father


def _create_interest_for_user(user, prop):
    if prop.deal_status == Property.DealStatus.SOLD:
        return None, "sold"
    interest, created = Interest.objects.get_or_create(customer=user, property=prop)
    if created:
        notify_father(interest)
        return interest, "created"
    return interest, "exists"


def _after_interest_redirect(request, interest, result):
    """After interest: show one-property WhatsApp send page (avoids double text)."""
    if result == "created" and interest is not None:
        return redirect("properties:interest_sent", pk=interest.pk)
    if result == "exists":
        messages.info(request, "You already showed interest in this property.")
    return redirect("properties:my_interests")


def home(request):
    featured = Property.objects.filter(is_active=True, is_featured=True)[:6]
    recent = Property.objects.filter(is_active=True).order_by("-created_at")[:8]
    return render(
        request,
        "properties/home.html",
        {"featured": featured, "recent": recent},
    )


def property_list(request):
    qs = Property.objects.filter(is_active=True)

    area = request.GET.get("area", "").strip()
    ptype = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()
    q = request.GET.get("q", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if area:
        qs = qs.filter(area=area)
    if ptype:
        qs = qs.filter(property_type=ptype)
    if status:
        qs = qs.filter(deal_status=status)
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(location_detail__icontains=q)
        )
    if min_price:
        try:
            qs = qs.filter(total_price__gte=Decimal(min_price))
        except (InvalidOperation, ValueError):
            pass
    if max_price:
        try:
            qs = qs.filter(total_price__lte=Decimal(max_price))
        except (InvalidOperation, ValueError):
            pass

    interested_ids = set()
    if request.user.is_authenticated:
        interested_ids = set(
            Interest.objects.filter(customer=request.user).values_list("property_id", flat=True)
        )

    return render(
        request,
        "properties/list.html",
        {
            "properties": qs,
            "areas": Property.Area.choices,
            "types": Property.PropertyType.choices,
            "statuses": Property.DealStatus.choices,
            "filters": {
                "area": area,
                "type": ptype,
                "status": status,
                "q": q,
                "min_price": min_price,
                "max_price": max_price,
            },
            "interested_ids": interested_ids,
        },
    )


def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk, is_active=True)
    already_interested = False
    if request.user.is_authenticated:
        already_interested = Interest.objects.filter(
            customer=request.user, property=prop
        ).exists()

    share_text = f"See this property in Vidarbha: {prop.title} - "
    share_url = request.build_absolute_uri(prop.get_absolute_url())
    wa_share = f"https://wa.me/?text={share_text}{share_url}"

    return render(
        request,
        "properties/detail.html",
        {
            "property": prop,
            "already_interested": already_interested,
            "wa_share": wa_share,
            "images": prop.images.all(),
        },
    )


@require_http_methods(["GET", "POST"])
def express_interest(request, pk):
    """Logged-in users send interest. Guests are sent to register/login first."""
    prop = get_object_or_404(Property, pk=pk, is_active=True)

    if not request.user.is_authenticated:
        request.session["pending_interest_property_id"] = prop.pk
        from django.urls import reverse

        return redirect(f"{reverse('accounts:auth_choice')}?next={reverse('properties:complete_interest')}")

    if request.method == "GET" and not request.GET.get("confirm"):
        return redirect(prop.get_absolute_url())

    interest, result = _create_interest_for_user(request.user, prop)
    if result == "sold":
        messages.warning(request, "This property is already sold.")
        return redirect(prop.get_absolute_url())
    return _after_interest_redirect(request, interest, result)


@login_required
def complete_interest(request):
    """After login/register, finish any pending “I’m Interested”."""
    pk = request.session.pop("pending_interest_property_id", None)
    if not pk:
        return redirect("properties:my_interests")

    prop = get_object_or_404(Property, pk=pk, is_active=True)
    interest, result = _create_interest_for_user(request.user, prop)
    if result == "sold":
        messages.warning(request, "This property is already sold.")
        return redirect(prop.get_absolute_url())
    return _after_interest_redirect(request, interest, result)


@login_required
def interest_sent(request, pk):
    """Confirm interest and let user send ONE WhatsApp message for this property."""
    interest = get_object_or_404(
        Interest.objects.select_related("property", "customer"),
        pk=pk,
        customer=request.user,
    )
    return render(
        request,
        "properties/interest_sent.html",
        {
            "interest": interest,
            "property": interest.property,
            "wa_url": interest_whatsapp_url(interest),
        },
    )


@login_required
def my_interests(request):
    interests = (
        Interest.objects.filter(customer=request.user)
        .select_related("property")
        .prefetch_related("property__images")
    )
    return render(request, "properties/my_interests.html", {"interests": interests})


def about(request):
    return render(request, "properties/about.html")
