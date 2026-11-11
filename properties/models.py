import re
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Property(models.Model):
    class PropertyType(models.TextChoices):
        PLOT = "plot", "Plot"
        FLAT = "flat", "Flat"
        HOUSE = "house", "House"
        SHOP = "shop", "Shop"
        FARM = "farm", "Farm"
        OTHER = "other", "Other"

    class DealStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        UNDER_NEGOTIATION = "under_negotiation", "Under Negotiation"
        SOLD = "sold", "Sold"

    class Area(models.TextChoices):
        # Vidarbha cities / districts
        NAGPUR = "nagpur", "Nagpur"
        AMRAVATI_CITY = "amravati_city", "Amravati"
        AKOLA = "akola", "Akola"
        YAVATMAL = "yavatmal", "Yavatmal"
        WARDHA = "wardha", "Wardha"
        CHANDRAPUR = "chandrapur", "Chandrapur"
        BHANDARA = "bhandara", "Bhandara"
        GONDIA = "gondia", "Gondia"
        WASHIM = "washim", "Washim"
        GADCHIROLI = "gadchiroli", "Gadchiroli"
        # Amravati region localities
        BADNERA = "badnera", "Badnera"
        DARYAPUR = "daryapur", "Daryapur"
        ACHALPUR = "achalpur", "Achalpur"
        MORSHI = "morshi", "Morshi"
        WARUD = "warud", "Warud"
        CHANDUR_BAZAR = "chandur_bazar", "Chandur Bazar"
        CHANDUR_RLY = "chandur_rly", "Chandur Railway"
        ANJANGAON = "anjangaon", "Anjangaon"
        DHAMANGAON = "dhamangaon", "Dhamangaon"
        TIWSA = "tiwsa", "Tiwsa"
        NANDGAON_KHANDESH = "nandgaon", "Nandgaon Khandeshwar"
        BHATKULI = "bhatkuli", "Bhatkuli"
        OTHER = "other", "Other (Vidarbha)"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    area = models.CharField(max_length=40, choices=Area.choices, default=Area.AMRAVATI_CITY)
    location_detail = models.CharField(
        max_length=255,
        blank=True,
        help_text="Landmark / society / road (optional)",
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.PLOT,
    )
    deal_status = models.CharField(
        max_length=20,
        choices=DealStatus.choices,
        default=DealStatus.AVAILABLE,
    )
    sq_ft = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    acres = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Used for farms. 1 acre = 43,560 sq ft.",
    )
    bhk = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} BHK") for i in range(1, 7)],
        help_text="Used for flats.",
    )
    price_per_sq_ft = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Leave blank to auto-calculate (sq ft × price per sq ft)",
    )
    youtube_url = models.URLField(blank=True)
    maps_url = models.URLField(blank=True, help_text="Google Maps link")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.price_per_sq_ft is None:
            self.price_per_sq_ft = 0
        if self.property_type != self.PropertyType.FARM:
            self.acres = None
        elif self.acres:
            self.sq_ft = max(1, int((self.acres * Decimal("43560")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        if self.property_type != self.PropertyType.FLAT:
            self.bhk = None
        elif not self.sq_ft:
            self.sq_ft = 1
        # Only auto-calc when a real rate is set (0 = call for price / hidden)
        if self.total_price is None and self.price_per_sq_ft and self.price_per_sq_ft > 0:
            if self.property_type == self.PropertyType.FARM and self.acres:
                self.total_price = (self.acres * self.price_per_sq_ft).quantize(Decimal("0.01"))
            elif self.sq_ft:
                self.total_price = self.sq_ft * self.price_per_sq_ft
        super().save(*args, **kwargs)

    @property
    def area_is_acres(self):
        return self.property_type == self.PropertyType.FARM

    @property
    def area_is_bhk(self):
        return self.property_type == self.PropertyType.FLAT

    @property
    def area_unit(self):
        if self.area_is_acres:
            return "acres"
        if self.area_is_bhk and self.bhk:
            return "bhk"
        return "sq_ft"

    @property
    def area_figure(self):
        """Public size: BHK for flats, acres for farms, square feet otherwise."""
        if self.area_unit == "bhk":
            return str(self.bhk)
        if self.area_is_acres:
            value = self.acres
            if value is None and self.sq_ft:
                value = (Decimal(self.sq_ft) / Decimal("43560")).quantize(Decimal("0.01"))
            if value is None:
                return ""
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return f"{self.sq_ft:,}"

    @property
    def price_on_request(self):
        """Public site never shows ₹ — customers call / WhatsApp the broker."""
        return True

    def get_absolute_url(self):
        return reverse("properties:detail", kwargs={"pk": self.pk})

    @property
    def location_display(self):
        base = self.get_area_display()
        if self.location_detail:
            return f"{self.location_detail}, {base}"
        return f"{base}, Vidarbha"

    @property
    def youtube_embed_id(self):
        if not self.youtube_url:
            return ""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return ""

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if img:
            return img
        return self.images.first()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="properties/%Y/%m/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.property_id}"


class Interest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CALLED = "called", "Called"
        CLOSED = "closed", "Closed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="interests",
        on_delete=models.CASCADE,
    )
    property = models.ForeignKey(Property, related_name="interests", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("customer", "property")
        verbose_name = "Interest"
        verbose_name_plural = "Interests"

    def __str__(self):
        return f"{self.customer.name} → {self.property.title}"
