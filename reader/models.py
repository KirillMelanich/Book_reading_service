from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year_of_publishing = models.PositiveIntegerField()
    last_time_read = models.DateTimeField(null=True, blank=True)
    short_description = models.TextField()
    long_description = models.TextField()

    def __str__(self):
        return f"'{self.title}' - {self.author}"


class ReadingSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def calculate_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def update_last_time_read(self):
        if self.end_time and (not self.book.last_time_read or self.book.last_time_read < self.end_time):
            self.book.last_time_read = self.end_time
            self.book.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_last_time_read()


@receiver(post_save, sender=ReadingSession)
def update_book_last_time_read(sender, instance, **kwargs):
    instance.update_last_time_read()
