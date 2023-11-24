from rest_framework import serializers
from .models import Book, ReadingSession, Profile


class BookSerializer(serializers.ModelSerializer):
    total_reading_time = serializers.SerializerMethodField()
    total_number_of_reading_sessions_for_all_users = serializers.SerializerMethodField()
    total_reading_time_for_all_users = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "year_of_publishing",
            "last_time_read",
            "total_reading_time",
            "total_number_of_reading_sessions_for_all_users",
            "total_reading_time_for_all_users",
            "short_description",
            "long_description",
        )
        read_only_fields = ("last_time_read", "total_reading_time", "total_number_of_reading_sessions_for_all_users", "total_reading_time_for_all_users",)
        extra_kwargs = {"long_description": {"write_only": True}}

    def get_total_reading_time(self, obj):
        user = self.context["request"].user
        return obj.total_reading_time_for_user(user)

    @staticmethod
    def get_total_number_of_reading_sessions_for_all_users(obj):
        return obj.total_number_of_reading_sessions_for_all_users()

    @staticmethod
    def get_total_reading_time_for_all_users(obj):
        return obj.total_reading_time_for_all_users()


class BookDetailSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "year_of_publishing",
            "last_time_read",
            "total_reading_time",
            "long_description",
            "total_number_of_reading_sessions_for_all_users",
            "total_reading_time_for_all_users",
        )


class ReadingSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        fields = "__all__"
        read_only_fields = ("end_time", "user")

    @staticmethod
    def get_duration(obj):
        return obj.calculate_duration()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "user",
            "number_of_reading_sessions",
            "last_activity",
            "total_reading_time",
            "last_book_read",
        )
        read_only_fields = (
            "user" "number_of_reading_sessions",
            "last_activity",
            "total_reading_time",
            "last_book_read",
        )


