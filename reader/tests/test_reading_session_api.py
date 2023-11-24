from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from reader.models import ReadingSession, Book, Profile

READING_SESSION_URL = reverse("reader:reading-session-list")


def detail_url(reading_session_id: int):
    return reverse("reader:reading-session-detail", args=[reading_session_id])


class ReadingSessionTestsUnauthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_access(self):
        # Ensure unauthenticated user cannot access reading sessions
        response = self.client.get(READING_SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Ensure unauthenticated user cannot create reading sessions
        payload = {"user": 1, "book": 1, "start_time": "2023-01-01T12:00:00Z"}
        response = self.client.post(READING_SESSION_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


        # Ensure unauthenticated user cannot delete reading sessions
        response = self.client.delete(detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_delete_reading_session_authenticated(self):
        book = self.create_book_sample()
        reading_session = self.create_reading_session_sample(self.user, book)
        url = detail_url(reading_session.id)

        # Save the initial state of the user's profile
        initial_profile = self.user.profile

        response = self.client.delete(url)

        # Assert the HTTP response status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert that the reading session is deleted
        self.assertEqual(ReadingSession.objects.count(), 0)

        # Assert that the user's profile is updated
        updated_profile = self.user.profile
        self.assertEqual(initial_profile.number_of_reading_sessions, updated_profile.number_of_reading_sessions)