from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from reader.models import ReadingSession


@receiver(post_save, sender=ReadingSession)
def update_book_last_time_read(sender, instance, **kwargs):
    instance.update_last_time_read()


@receiver(post_save, sender=ReadingSession)
def update_profile_last_activity(sender, instance, **kwargs):
    instance.user.profile.last_activity = instance.start_time
    instance.user.profile.save()


# Signal to update the last_book_read when a ReadingSession is saved
@receiver(post_save, sender=ReadingSession)
def update_profile_last_book_read(sender, instance, **kwargs):
    profile = instance.user.profile
    profile.update_reading_sessions_count()


# Signal to handle the deletion of a ReadingSession and update last_book_read accordingly
@receiver(pre_delete, sender=ReadingSession)
def handle_deleted_reading_session(sender, instance, **kwargs):
    profile = instance.user.profile
    profile.update_reading_sessions_count()
