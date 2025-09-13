# managementapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from dashboard.models import ManageMember
from users.models import UserProfile  # adjust if needed

@receiver(post_save, sender=User)
def create_manage_member(sender, instance, created, **kwargs):
    if created:
        profile = None
        try:
            profile = UserProfile.objects.get(user=instance)
        except UserProfile.DoesNotExist:
            pass

        ManageMember.objects.create(
            member=instance,
            profile=profile,
            status=True  # default active
        )
