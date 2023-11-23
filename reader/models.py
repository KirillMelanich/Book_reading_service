from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year_of_publishing = models.PositiveIntegerField()
    last_time_read = models.DateTimeField(null=True, blank=True)
    short_description = models.TextField()
    long_description = models.TextField()

    def __str__(self):
        return f"{self.id}"

    def total_reading_time_for_user(self, user):
        sessions = ReadingSession.objects.filter(
            user=user, book=self, end_time__isnull=False
        )
        total_duration = sum(
            (session.calculate_duration() for session in sessions), timedelta()
        )
        return total_duration


class ReadingSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def calculate_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def update_last_time_read(self):
        if self.end_time and (
            not self.book.last_time_read or self.book.last_time_read < self.end_time
        ):
            self.book.last_time_read = self.end_time
            self.book.save()

    def stop_reading(self):
        if not self.end_time:
            self.end_time = timezone.now()
            self.save()
            # # Update the number_of_reading_sessions in the associated Profile
            # self.user.profile.update_reading_sessions_count()

    def save(self, *args, **kwargs):
        if not self.pk:
            # Check if the user already has an active session for this book
            active_sessions = ReadingSession.objects.filter(
                user=self.user, book=self.book, end_time=None
            )
            if active_sessions.exists():
                # If there is an active session, stop it before starting a new one
                active_sessions.first().stop_reading()

        super().save(*args, **kwargs)


@receiver(post_save, sender=ReadingSession)
def update_book_last_time_read(sender, instance, **kwargs):
    instance.update_last_time_read()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_activity = models.DateTimeField(null=True, blank=True)
    number_of_reading_sessions = models.PositiveIntegerField(default=0)
    total_reading_time = models.DurationField(default=timezone.timedelta)

    def update_reading_sessions_count(self):
        # Count the number of reading sessions for the user
        count = ReadingSession.objects.filter(user=self.user).count()
        self.number_of_reading_sessions = count

        # Calculate the total reading time for the user
        sessions = ReadingSession.objects.filter(user=self.user, end_time__isnull=False)
        total_duration = sum(
            (session.calculate_duration() for session in sessions), timedelta()
        )
        self.total_reading_time = total_duration

        self.save()


@receiver(post_save, sender=ReadingSession)
def update_profile_last_activity(sender, instance, **kwargs):
    instance.user.profile.last_activity = instance.start_time
    instance.user.profile.save()
