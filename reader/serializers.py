from rest_framework import serializers
from .models import Book, ReadingSession, Profile


class BookSerializer(serializers.ModelSerializer):
    total_reading_time_for_user = serializers.SerializerMethodField()
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
            "total_reading_time_for_user",
            "total_number_of_reading_sessions_for_all_users",
            "total_reading_time_for_all_users",
            "short_description",
            "long_description",
        )
        read_only_fields = (
            "last_time_read",
            "total_reading_time_for_user",
            "total_number_of_reading_sessions_for_all_users",
            "total_reading_time_for_all_users",
        )
        extra_kwargs = {"long_description": {"write_only": True}}

    def get_total_reading_time_for_user(self, obj):
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
            "total_reading_time_for_user",
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

    def create(self, validated_data):
        # Set the 'user' field based on the logged-in user
        user = self.context["request"].user
        validated_data["user"] = user

        # Create the reading session instance
        reading_session = super().create(validated_data)

        # Update the number_of_reading_sessions and last_activity in the associated Profile
        profile = user.profile
        profile.update_reading_sessions_count()
        profile.calculate_total_reading_time_for_user()
        profile.get_last_book_read()
        profile.last_activity = reading_session.start_time
        profile.save()

        return reading_session


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
            "user",
            "number_of_reading_sessions",
            "last_activity",
            "total_reading_time",
            "last_book_read",
        )


# Django channels
# adding extra services
