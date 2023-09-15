from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Books
from books.serializers import BooksSerializer

BOOK_URL = reverse("books:books-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample Author",
        "cover": "HARD",
        "inventory": 1,
        "daily_fee": 10,
    }
    defaults.update(params)
    return Books.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:books-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_required_book(self):
        res = self.client.get(BOOK_URL)
        book = Books.objects.order_by("id")
        serializer = BooksSerializer(book, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Sample book",
            "author": "Sample Author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 10,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Books.objects.order_by("id")
        serializer = BooksSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BooksSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Sample book",
            "author": "Sample Author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 10,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_forbidden(self):
        payload = {
            "title": "Sample book",
            "author": "Sample Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 100,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_not_allowed(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_str(self):
        book = sample_book()
        self.assertEqual(str(book), "Sample book, Author: Sample Author")


class AdminBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Sample book",
            "author": "Sample Author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 10,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Books.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_put_book_allowed(self):
        payload = {
            "title": "Sample book",
            "author": "Sample Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 100,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_book_allowed(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
