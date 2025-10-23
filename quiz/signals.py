# quiz/signals.py
# ----------------
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile  # adjust import path if your app name differs

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    """
    Guarantee that every User has a matching UserProfile.
    If one already exists, do nothing; otherwise create it.
    The new profile model handles default values internally.
    """
    UserProfile.objects.get_or_create(user=instance)