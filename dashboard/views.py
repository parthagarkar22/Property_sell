from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from properties.message_parser import parse_property_message
from properties.models import Interest, Property, PropertyImage

from .decorators import broker_required
from .forms import BrokerLoginForm, EasyPropertyMessageForm, InterestStatusForm, PropertyForm

_PROPERTY_FORM_KEYS = {
    "title",
    "description",
    "area",
    "location_detail",
    "property_type",
    "deal_status",
    "sq_ft",
    "acres",
    "bhk",
    "price_per_sq_ft",
    "total_price",
    "youtube_url",
    "maps_url",
    "is_active",
    "is_featured",
}


def broker_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("dashboard:home")

    form = BrokerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"].strip()
        password = form.cleaned_data["password"]
        user = authenticate(request, username=phone, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f"Welcome, {user.name}!")
            return redirect("dashboard:home")
        messages.error(request, "Wrong phone or password, or not a broker account.")

    return render(request, "dashboard/login.html", {"form": form})


@require_POST
def broker_logout(request):
    logout(request)
    messages.info(request, "Logged out of broker dashboard.")
    return redirect("dashboard:login")


@broker_required
def home(request):
    stats = {
        "properties": Property.objects.count(),
        "active": Property.objects.filter(is_active=True).count(),
        "new_interests": Interest.objects.filter(status=Interest.Status.NEW).count(),
        "total_interests": Interest.objects.count(),
    }
    recent_interests = (
        Interest.objects.select_related("customer", "property").order_by("-created_at")[:8]
    )
    recent_properties = Property.objects.order_by("-updated_at")[:6]
    return render(
        request,
        "dashboard/home.html",
        {
            "stats": stats,
            "recent_interests": recent_interests,
            "recent_properties": recent_properties,
        },
    )


@broker_required
def property_list(request):
    q = request.GET.get("q", "").strip()
    qs = Property.objects.annotate(image_count=Count("images")).order_by("-updated_at")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(location_detail__icontains=q))
    return render(request, "dashboard/property_list.html", {"properties": qs, "q": q})


def _save_uploaded_images(prop, files):
    for index, image in enumerate(files):
        if not image:
            continue
        PropertyImage.objects.create(
            property=prop,
            image=image,
            is_primary=(not prop.images.exists() and index == 0),
            order=prop.images.count() + index,
        )


def _property_form_data_from_parsed(parsed: dict) -> dict:
    data = {k: parsed[k] for k in _PROPERTY_FORM_KEYS if k in parsed and parsed[k] is not None}
    # Required numeric defaults so ModelForm can validate after easy-add edge cases
    if "sq_ft" not in data or not data["sq_ft"]:
        data["sq_ft"] = 1
    if "price_per_sq_ft" not in data or data["price_per_sq_ft"] is None:
        data["price_per_sq_ft"] = 0
    data.setdefault("is_active", True)
    data.setdefault("is_featured", False)
    data.setdefault("youtube_url", "")
    data.setdefault("maps_url", "")
    return data


@broker_required
def property_easy_add(request):
    """Paste Marathi WhatsApp message → create property (minimal fields for father)."""
    form = EasyPropertyMessageForm(request.POST or None, request.FILES or None)
    preview = None

    if request.method == "POST" and form.is_valid():
        parsed = parse_property_message(form.cleaned_data["message"])
        # Price stays hidden on website — customers call broker
        parsed["price_per_sq_ft"] = 0
        parsed["total_price"] = None
        form_data = _property_form_data_from_parsed(parsed)
        prop_form = PropertyForm(form_data)

        if prop_form.is_valid():
            prop = prop_form.save()
            _save_uploaded_images(prop, request.FILES.getlist("images"))
            warn = parsed.get("warnings") or []
            if warn:
                messages.warning(
                    request,
                    "प्रॉपर्टी सेव्ह झाली. तपासा: " + " · ".join(warn),
                )
            else:
                messages.success(request, "प्रॉपर्टी सेव्ह झाली! / Property added.")
            return redirect("dashboard:property_edit", pk=prop.pk)

        # Could not auto-save (e.g. missing sq ft) — show review form
        messages.info(
            request,
            "मेसेज वाचला. खालील फॉर्म तपासा व सेव्ह करा. / Review and save below.",
        )
        return render(
            request,
            "dashboard/property_form.html",
            {
                "form": prop_form,
                "property_obj": None,
                "images": [],
                "from_message": True,
                "parsed_warnings": parsed.get("warnings") or [],
                "raw_message": form.cleaned_data["message"],
            },
        )

    return render(
        request,
        "dashboard/property_easy_add.html",
        {"form": form, "preview": preview},
    )


@broker_required
@require_POST
def property_apply_message(request, pk):
    """Update an existing property from a pasted Marathi message."""
    prop = get_object_or_404(Property, pk=pk)
    message = (request.POST.get("message") or "").strip()
    if not message:
        messages.error(request, "मेसेज पेस्ट करा.")
        return redirect("dashboard:property_edit", pk=pk)

    parsed = parse_property_message(message)
    # Keep existing prices if message has none
    if parsed.get("price_per_sq_ft") is None:
        parsed["price_per_sq_ft"] = prop.price_per_sq_ft
    if parsed.get("total_price") is None:
        parsed["total_price"] = prop.total_price
    if not parsed.get("sq_ft"):
        parsed["sq_ft"] = prop.sq_ft
    if parsed.get("acres") is None and prop.acres:
        parsed["acres"] = prop.acres
    if parsed.get("bhk") is None and prop.bhk:
        parsed["bhk"] = prop.bhk

    form_data = _property_form_data_from_parsed(parsed)
    # Preserve media links / flags unless we want to overwrite description etc.
    form_data["youtube_url"] = prop.youtube_url
    form_data["maps_url"] = prop.maps_url
    form_data["is_active"] = prop.is_active
    form_data["is_featured"] = prop.is_featured

    prop_form = PropertyForm(form_data, instance=prop)
    if prop_form.is_valid():
        prop_form.save()
        warn = parsed.get("warnings") or []
        if warn:
            messages.warning(request, "अपडेट झाले. तपासा: " + " · ".join(warn))
        else:
            messages.success(request, "मेसेजनुसार प्रॉपर्टी अपडेट झाली.")
    else:
        messages.error(request, "मेसेजमधून अपडेट करता आले नाही. फॉर्म तपासा.")
    return redirect("dashboard:property_edit", pk=pk)


@broker_required
def property_create(request):
    form = PropertyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save()
        _save_uploaded_images(prop, request.FILES.getlist("images"))
        messages.success(request, "Property added successfully.")
        return redirect("dashboard:property_edit", pk=prop.pk)
    return render(
        request,
        "dashboard/property_form.html",
        {"form": form, "property_obj": None, "images": []},
    )


@broker_required
def property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    form = PropertyForm(request.POST or None, instance=prop)
    if request.method == "POST" and form.is_valid():
        prop = form.save()
        _save_uploaded_images(prop, request.FILES.getlist("images"))
        messages.success(request, "Property saved.")
        return redirect("dashboard:property_edit", pk=prop.pk)
    return render(
        request,
        "dashboard/property_form.html",
        {
            "form": form,
            "property_obj": prop,
            "images": prop.images.all(),
        },
    )


@broker_required
@require_POST
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    title = prop.title
    prop.delete()
    messages.success(request, f"Deleted: {title}")
    return redirect("dashboard:property_list")


@broker_required
@require_POST
def image_delete(request, pk):
    img = get_object_or_404(PropertyImage, pk=pk)
    prop_id = img.property_id
    img.delete()
    messages.success(request, "Photo removed.")
    return redirect("dashboard:property_edit", pk=prop_id)


@broker_required
@require_POST
def image_set_primary(request, pk):
    img = get_object_or_404(PropertyImage, pk=pk)
    PropertyImage.objects.filter(property_id=img.property_id).update(is_primary=False)
    img.is_primary = True
    img.save(update_fields=["is_primary"])
    messages.success(request, "Main photo updated.")
    return redirect("dashboard:property_edit", pk=img.property_id)


@broker_required
def interest_list(request):
    status = request.GET.get("status", "").strip()
    qs = Interest.objects.select_related("customer", "property").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return render(
        request,
        "dashboard/interest_list.html",
        {
            "interests": qs,
            "status_filter": status,
            "status_choices": Interest.Status.choices,
        },
    )


@broker_required
@require_POST
def interest_update_status(request, pk):
    interest = get_object_or_404(Interest, pk=pk)
    form = InterestStatusForm(request.POST, instance=interest)
    if form.is_valid():
        form.save()
        messages.success(request, "Interest status updated.")
    else:
        messages.error(request, "Could not update status.")
    next_url = request.POST.get("next") or "dashboard:interest_list"
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("dashboard:interest_list")
