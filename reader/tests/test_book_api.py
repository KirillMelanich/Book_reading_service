from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from reader.models import Book

BOOK_URL = reverse("reader:book-list")


def detail_url(book_id: int):
    return reverse("reader:book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "John Doe",
        "year_of_publishing": 2022,
        "short_description": "A short description",
        "long_description": "A long description",
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Sample Book",
            "author": "John Doe",
            "year_of_publishing": 2022,
            "short_description": "A short description",
            "long_description": "A long description",
        }

        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.year_of_publishing, payload["year_of_publishing"])
        self.assertEqual(book.short_description, payload["short_description"])
        self.assertEqual(book.long_description, payload["long_description"])

    def test_create_book_with_read_only_fields(self):
        payload = {
            "title": "Sample Book",
            "author": "John Doe",
            "year_of_publishing": 2022,
            "short_description": "A short description",
            "long_description": "A long description",
            "last_time_read": "2023-01-01T12:00:00",
        }

        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.year_of_publishing, payload["year_of_publishing"])
        self.assertEqual(book.short_description, payload["short_description"])
        self.assertEqual(book.long_description, payload["long_description"])
        self.assertIsNone(book.last_time_read)  # last_time_read should be None

    def test_update_book(self):
        book = Book.objects.create(
            title="Old Title",
            author="Old Author",
            year_of_publishing=2020,
            short_description="Old Short Description",
            long_description="Old Long Description",
        )

        payload = {
            "title": "Updated Title",
            "author": "Updated Author",
            "year_of_publishing": 2021,
            "short_description": "Updated Short Description",
            "long_description": "Updated Long Description",
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.year_of_publishing, payload["year_of_publishing"])
        self.assertEqual(book.short_description, payload["short_description"])
        self.assertEqual(book.long_description, payload["long_description"])

    def test_delete_book(self):
        book = Book.objects.create(
            title="Sample Book",
            author="John Doe",
            year_of_publishing=2022,
            short_description="A short description",
            long_description="A long description",
        )

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_unauthorized(self):
        payload = {
            "title": "Sample Book",
            "author": "John Doe",
            "year_of_publishing": 2022,
            "short_description": "A short description",
            "long_description": "A long description",
        }

        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_unauthorized(self):
        book = sample_book()
        payload = {
            "title": "Updated Title",
            "author": "Updated Author",
            "year_of_publishing": 2021,
            "short_description": "Updated Short Description",
            "long_description": "Updated Long Description",
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_unauthorized(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books_authenticated(self):
        sample_book()
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_unauthorized(self):
        payload = {
            "title": "Sample Book",
            "author": "John Doe",
            "year_of_publishing": 2022,
            "short_description": "A short description",
            "long_description": "A long description",
        }

        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_unauthorized(self):
        book = sample_book()
        payload = {
            "title": "Updated Title",
            "author": "Updated Author",
            "year_of_publishing": 2021,
            "short_description": "Updated Short Description",
            "long_description": "Updated Long Description",
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_unauthorized(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

