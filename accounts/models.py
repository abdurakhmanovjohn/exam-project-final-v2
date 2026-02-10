# pyright:reportOperatorIssue=false
# pyright:reportIncompatibleVariableOverride=false
# pyright:reportIncompatibleMethodOverride=false
# pyright:reportArgumentType=false

from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

UZ_PHONE_REGEX = r"^(?:\+998)?[ -]?\d{2}[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}$"

phone_validator = RegexValidator(
    regex=UZ_PHONE_REGEX,
    message=_("Phone number must be in format: '+998 XX XXX XX XX'"),
)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        unique=True,
        validators=[phone_validator],
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    language = models.CharField(
        max_length=2,
        choices=[("en", "English"), ("uz", "Uzbek"), ("ru", "Russian")],
        default="en",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return self.get_full_name() or self.phone_number

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class VerificationCode(models.Model):
    phone_number = models.CharField(max_length=20, validators=[phone_validator])
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    OTP_LIFETIME_MINUTES = 5

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(
            minutes=self.OTP_LIFETIME_MINUTES
        )

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
