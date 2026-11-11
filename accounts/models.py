from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$",
    message="Enter a valid 10-digit Indian mobile number.",
)


class CustomerManager(BaseUserManager):
    def create_user(self, phone, name="", password=None, **extra):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, name=name or phone, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name="Admin", password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_verified", True)
        if password is None:
            raise ValueError("Superuser must have a password")
        user = self.create_user(phone=phone, name=name, password=password, **extra)
        return user


class Customer(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=10, unique=True, validators=[phone_validator])
    name = models.CharField(max_length=120)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomerManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.name} ({self.phone})"
