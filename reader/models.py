from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import ExpressionWrapper, Sum, F, fields
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, default="Unknown author")
    year_of_publishing = models.PositiveIntegerField(blank=True)
    last_time_read = models.DateTimeField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.id}"

    def total_reading_time_for_user(self, user):
        total_duration = ReadingSession.objects.filter(
            user=user, book=self, end_time__isnull=False
        ).aggregate(
            total_duration=ExpressionWrapper(
                Sum(F("end_time") - F("start_time")),
                output_field=fields.DurationField(),
            )
        )["total_duration"] or timedelta()

        return total_duration

    def total_number_of_reading_sessions_for_all_users(self):
        return ReadingSession.objects.filter(book=self).count()

    def total_reading_time_for_all_users(self):
        total_duration = ReadingSession.objects.filter(
             book=self, end_time__isnull=False
        ).aggregate(
            total_duration=ExpressionWrapper(
                Sum(F("end_time") - F("start_time")),
                output_field=fields.DurationField(),
            )
        )["total_duration"] or timedelta()

        return total_duration


class ReadingSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

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


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_activity = models.DateTimeField(null=True, blank=True)
    number_of_reading_sessions = models.PositiveIntegerField(default=0)
    total_reading_time = models.DurationField(default=timezone.timedelta)
    last_book_read = models.ForeignKey(
        "Book", null=True, blank=True, on_delete=models.SET_NULL
    )

    def update_reading_sessions_count(self):
        # Count the number of reading sessions for the user
        count = ReadingSession.objects.filter(user=self.user).count()
        self.number_of_reading_sessions = count

        self.save()

    def calculate_total_reading_time_for_user(self):
        total_duration = ReadingSession.objects.filter(
            user=self.user, end_time__isnull=False
        ).aggregate(
            total_duration=ExpressionWrapper(
                Sum(F("end_time") - F("start_time")),
                output_field=fields.DurationField(),
            )
        )["total_duration"] or timedelta()

        self.total_reading_time = total_duration
        self.save()

    def get_last_book_read(self):
        last_reading_session = (
            ReadingSession.objects.filter(user=self.user, end_time__isnull=False)
            .order_by("-end_time")
            .first()
        )

        if last_reading_session:
            self.last_book_read = last_reading_session.book
        else:
            self.last_book_read = None

        self.save()
