from rest_framework import serializers
from .models import Book, ReadingSession


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("last_time_read", )
        extra_kwargs = {"long_description": {"write_only": True}}


class BookDetailSerializer(BookSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "year_of_publishing", "last_time_read", "long_description")


class ReadingSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        exclude = ('user',)  # Exclude the 'user' field
        read_only_fields = ("end_time", )

    def get_duration(self, obj):
        return obj.calculate_duration()
