from django.conf import settings
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    short_description = models.TextField()
    total_reading_time = models.DurationField(default=0)

    def __str__(self):
        return f"'{self.title}' - {self.author}"


class ReadingSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def calculate_duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the total_reading_time field of the associated book
        total_duration = sum([session.calculate_duration() for session in self.book.readingsession_set.all() if session.calculate_duration()])
        self.book.total_reading_time = total_duration
        self.book.save()