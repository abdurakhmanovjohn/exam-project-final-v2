# pyright: reportAttributeAccessIssue=false

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wallet

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_default_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(
            user=instance,
            name="Cash",
            currency="UZS",
            balance=0,
        )
