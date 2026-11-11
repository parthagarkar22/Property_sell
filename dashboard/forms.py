from decimal import Decimal, ROUND_HALF_UP

from django import forms

from properties.models import Interest, Property, PropertyImage


class BrokerLoginForm(forms.Form):
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "dash-input",
                "placeholder": "10-digit mobile",
                "inputmode": "numeric",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "dash-input",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )


class _AutoTrimCharField(forms.CharField):
    """Trim to max_length before Django's length validator runs."""

    def to_python(self, value):
        value = super().to_python(value)
        if value and self.max_length and len(value) > self.max_length:
            return value[: self.max_length - 1].rstrip() + "…"
        return value


class PropertyForm(forms.ModelForm):
    title = _AutoTrimCharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "dash-input", "placeholder": "Property title"}),
    )
    location_detail = _AutoTrimCharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "dash-input", "placeholder": "Landmark / society / road"}
        ),
    )

    class Meta:
        model = Property
        fields = [
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
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={"class": "dash-input", "rows": 5, "placeholder": "Full details for customers"}
            ),
            "area": forms.Select(attrs={"class": "dash-input"}),
            "property_type": forms.Select(attrs={"class": "dash-input"}),
            "deal_status": forms.Select(attrs={"class": "dash-input"}),
            "sq_ft": forms.NumberInput(attrs={"class": "dash-input", "min": 1, "step": "1"}),
            "acres": forms.NumberInput(
                attrs={"class": "dash-input", "min": "0.01", "step": "0.01", "placeholder": "e.g. 2.5"}
            ),
            "bhk": forms.Select(attrs={"class": "dash-input"}),
            "price_per_sq_ft": forms.NumberInput(
                attrs={
                    "class": "dash-input",
                    "min": 0,
                    "step": "0.01",
                    "placeholder": "Optional — not shown on website",
                }
            ),
            "total_price": forms.NumberInput(
                attrs={
                    "class": "dash-input",
                    "min": 0,
                    "step": "0.01",
                    "placeholder": "Optional — not shown on website",
                }
            ),
            "youtube_url": forms.URLInput(
                attrs={"class": "dash-input", "placeholder": "https://youtube.com/watch?v=..."}
            ),
            "maps_url": forms.URLInput(
                attrs={"class": "dash-input", "placeholder": "Google Maps link"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "dash-check"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "dash-check"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Price is never required — website shows “Call for price”
        self.fields["price_per_sq_ft"].required = False
        self.fields["total_price"].required = False
        self.fields["sq_ft"].required = False
        self.fields["acres"].required = False
        self.fields["bhk"].required = False
        if (
            self.instance.pk
            and self.instance.property_type == Property.PropertyType.FARM
            and not self.instance.acres
            and self.instance.sq_ft
            and "acres" not in self.initial
        ):
            self.initial["acres"] = (Decimal(self.instance.sq_ft) / Decimal("43560")).quantize(
                Decimal("0.01")
            )

    def clean_price_per_sq_ft(self):
        value = self.cleaned_data.get("price_per_sq_ft")
        if value in (None, ""):
            return 0
        return value

    def clean_total_price(self):
        value = self.cleaned_data.get("total_price")
        if value in (None, ""):
            return None
        return value

    def clean(self):
        cleaned = super().clean()
        ptype = cleaned.get("property_type")
        if ptype == Property.PropertyType.FARM:
            cleaned["bhk"] = None
            acres = cleaned.get("acres")
            if not acres:
                self.add_error("acres", "Enter the farm size in acres.")
            else:
                cleaned["sq_ft"] = max(
                    1,
                    int((acres * Decimal("43560")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
                )
        elif ptype == Property.PropertyType.FLAT:
            cleaned["acres"] = None
            if not cleaned.get("bhk"):
                self.add_error("bhk", "Select BHK for this flat.")
            elif not cleaned.get("sq_ft"):
                if self.instance.pk and self.instance.sq_ft:
                    cleaned["sq_ft"] = self.instance.sq_ft
                else:
                    cleaned["sq_ft"] = 1
        else:
            cleaned["acres"] = None
            cleaned["bhk"] = None
            if not cleaned.get("sq_ft"):
                self.add_error("sq_ft", "Enter the size in square feet.")
        return cleaned


class MultiImageUploadForm(forms.Form):
    images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "dash-input", "accept": "image/*"}),
        help_text="You can select multiple photos (JPG/PNG).",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["images"].widget.attrs["multiple"] = True


class InterestStatusForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "dash-input dash-status"}),
        }


class EasyPropertyMessageForm(forms.Form):
    """Father-friendly: paste WhatsApp message (no price — call for price on site)."""

    message = forms.CharField(
        label="मेसेज पेस्ट करा",
        widget=forms.Textarea(
            attrs={
                "class": "dash-input easy-message",
                "rows": 8,
                "placeholder": "WhatsApp मधील संपूर्ण प्रॉपर्टी मेसेज इथे पेस्ट करा…",
            }
        ),
    )
    images = forms.FileField(
        label="फोटो (ऐच्छिक)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "dash-input", "accept": "image/*"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["images"].widget.attrs["multiple"] = True
