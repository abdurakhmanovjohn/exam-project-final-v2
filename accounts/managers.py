from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def normalize_phone(self, phone):
        return phone.replace(" ", "").replace("-", "")

    def create_user(self, phone_number, first_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_("Phone number is required"))

        phone_number = self.normalize_phone(phone_number)

        user = self.model(
            phone_number=phone_number, first_name=first_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, first_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(phone_number, first_name, password, **extra_fields)
