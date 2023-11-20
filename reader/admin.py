from django.contrib import admin

from reader.models import Book, ReadingSession

admin.site.register(Book)
admin.site.register(ReadingSession)
