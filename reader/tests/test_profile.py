from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from reader.models import Profile, ReadingSession, Book

PROFILE_URL = reverse("reader:profile-list")


class ProfileTestsUnauthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_access(self):
        # Ensure unauthenticated user cannot access profiles
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTestsAuthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(user=self.user)

        # Create a profile for the user
        Profile.objects.get_or_create(user=self.user)

    def test_authenticated_access(self):
        # Ensure authenticated user can access their own profile
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_profile_authenticated(self):
        # Ensure a profile is automatically created for the user upon registration
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.count(), 1)

    def test_update_profile_authenticated(self):
        # Ensure authenticated user can not update his profile
        updated_data = {"last_activity": "2023-01-02T12:00:00Z"}
        response = self.client.patch(PROFILE_URL, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Assert that the profile data is not updated
        updated_profile = Profile.objects.get(user=self.user)
        self.assertNotEquals(updated_profile.last_activity, "2023-01-02T12:00:00Z")

    def test_delete_profile_authenticated(self):
        # Ensure authenticated user cannot delete their own profile
        response = self.client.delete(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProfileMethodsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.book = Book.objects.create(
            title="Sample Book",
            author="Sample Author",
            year_of_publishing=2022,
            short_description="Sample Short Description",
            long_description="Sample Long Description",
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_update_reading_sessions_count(self):
        # Create a reading session for the user
        ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )

        # Call the method to update reading sessions count
        self.profile.update_reading_sessions_count()

        # Assert that the reading sessions count is updated
        self.assertEqual(self.profile.number_of_reading_sessions, 1)

    def test_calculate_total_reading_time_for_user(self):
        # Create a reading session with duration for the user
        ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )

        # Call the method to calculate total reading time
        self.profile.calculate_total_reading_time_for_user()

        # Assert that the total reading time is updated
        expected_duration = timedelta(hours=1)
        actual_duration = self.profile.total_reading_time

        # Allow a small time difference (e.g., 1 second) for comparison
        allowed_difference = timedelta(seconds=1)
        self.assertTrue(
            expected_duration - allowed_difference <= actual_duration <= expected_duration + allowed_difference
        )

    def test_get_last_book_read(self):
        # Create a reading session for the user with the last book read
        last_book = Book.objects.create(
            title="Last Book",
            author="Last Author",
            year_of_publishing=2021,
            short_description="Last Short Description",
            long_description="Last Long Description",
        )
        ReadingSession.objects.create(
            user=self.user,
            book=last_book,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )

        # Call the method to get the last book read
        self.profile.get_last_book_read()

        # Assert that the last book read is updated
        self.assertEqual(self.profile.last_book_read, last_book)