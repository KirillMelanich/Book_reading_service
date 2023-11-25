from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from reader.models import Profile

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