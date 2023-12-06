from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from reader.models import Profile


@receiver(post_save, sender=User)
# Creates a profile instance right after ner user is registered
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
