from rest_framework import serializers
from .models import Book, ReadingSession


class BookSerializer(serializers.ModelSerializer):
    total_reading_time = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "year_of_publishing", "last_time_read", "total_reading_time", "short_description")
        read_only_fields = ("last_time_read", "total_reading_time")
        extra_kwargs = {"long_description": {"write_only": True}}

    def get_total_reading_time(self, obj):
        user = self.context['request'].user
        return obj.total_reading_time_for_user(user)


class BookDetailSerializer(BookSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "year_of_publishing", "last_time_read", "total_reading_time", "long_description")


class ReadingSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        exclude = ('user',)  # Exclude the 'user' field
        read_only_fields = ("end_time", )

    def get_duration(self, obj):
        return obj.calculate_duration()
