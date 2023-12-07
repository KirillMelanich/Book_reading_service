from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from reader.models import ReadingSession, Book, Profile

READING_SESSION_URL = reverse("reader:reading-session-list")


def detail_url(reading_session_id: int):
    return reverse("reader:reading-session-detail", args=[reading_session_id])


class ReadingSessionTestsAuthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(user=self.user)

        # Create a profile for the user
        Profile.objects.get_or_create(user=self.user)

        self.client.force_authenticate(user=self.user)

    @staticmethod
    def create_book_sample():
        return Book.objects.create(
            title="Sample Book",
            author="Sample Author",
            year_of_publishing=2022,
            short_description="Sample Short Description",
            long_description="Sample Long Description",
        )

    @staticmethod
    def create_reading_session_sample(user, book):
        return ReadingSession.objects.create(
            user=user,
            book=book,
            start_time="2023-01-01T12:00:00Z",
        )

    def test_authenticated_access(self):
        # Ensure authenticated user can access reading sessions
        response = self.client.get(READING_SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_reading_session_authenticated(self):
        book = self.create_book_sample()
        payload = {
            "user": self.user.id,
            "book": book.id,
            "start_time": "2023-01-01T12:00:00Z",
            "end_time": "2023-01-01T13:00:00Z",
        }
        response = self.client.post(READING_SESSION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReadingSession.objects.count(), 1)
        self.assertEqual(response.data["user"], self.user.id)


class ReadingSessionMethodsTests(TestCase):
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
        self.reading_session = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            start_time=timezone.now(),
            end_time=None,
        )

    def test_calculate_duration(self):
        # Create a reading session with start and end times
        session_with_duration = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )
        calculated_duration = session_with_duration.calculate_duration()

        # Allow a small time difference (e.g., 1 second) for comparison
        allowed_difference = timedelta(seconds=1)
        self.assertTrue(
            timedelta(hours=1) - allowed_difference
            <= calculated_duration
            <= timedelta(hours=1) + allowed_difference
        )

        # Create a reading session without end time
        self.assertIsNone(self.reading_session.calculate_duration())

    def test_stop_reading(self):
        # Create a reading session without end time
        self.reading_session.stop_reading()

        # Assert that the reading session's end time is set
        self.assertIsNotNone(self.reading_session.end_time)

        # Assert that the book's last_time_read is updated
        self.assertEqual(self.book.last_time_read, self.reading_session.end_time)

        # Create a reading session with end time
        session_with_end_time = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            start_time=timezone.now(),
            end_time=timezone.now() - timedelta(days=1),
        )

        # Save the initial end time with microsecond precision
        initial_end_time = session_with_end_time.end_time.replace(microsecond=0)

        session_with_end_time.stop_reading()

        # Assert that the reading session's end time is not updated
        updated_end_time = session_with_end_time.end_time.replace(microsecond=0)
        self.assertEqual(updated_end_time, initial_end_time)


