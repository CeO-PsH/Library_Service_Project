from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from books.models import Books
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingDetailSerializer


BORROWINGS_URL = reverse("borrowing:borrowing-list")


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

def sample_borrowing(**params):
    book = sample_book()
    defaults = {
        "borrow_date": "2023-09-10T15:39:57.710Z",
        "expected_return_date": datetime.now() + timedelta(days=2),
        "book": book,
        "is_active": True,
        "user": None
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)

def detail_url(borrowings_id):
    return reverse("borrowing:borrowing-detail", args=[borrowings_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_borrowing(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        user = self.user
        sample_borrowing(user=user)
        sample_borrowing(user=user)

        res = self.client.get(BORROWINGS_URL)

        borrowing = Borrowing.objects.order_by("id")
        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


    def test_filter_borrowing_by_active(self):
        user = self.user
        borrowing1 = sample_borrowing(user=user, is_active=True)
        borrowing2 = sample_borrowing(user=user, is_active=True)

        borrowing3 = sample_borrowing(user=user, is_active=False)

        res = self.client.get(
            BORROWINGS_URL, {"is_active": True}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_borrowing_detail(self):
        user = self.user
        borrowing = sample_borrowing(user=user)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        book = sample_book()
        payload = {
            "expected_return_date": "2023-09-15T15:39:57.710Z",
            "book": book.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_borrowing_validation(self):
        book = sample_book(inventory=0)
        payload = {
            "expected_return_date": "2023-09-15T15:39:57.710Z",
            "book": book.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_without_book(self):
        payload = {
            "expected_return_date": "2023-09-15T15:39:57.710Z",
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_return_borrowing(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        url = reverse("borrowing:return_borrowing", args=[borrowing.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)

        updated_borrowing = Borrowing.objects.get(pk=borrowing.pk)
        self.assertFalse(updated_borrowing.is_active)
        self.assertEqual(updated_borrowing.book.inventory, 2)

    def test_return_already_returned_borrowing(self):
        user = self.user
        already_returned_borrowing = sample_borrowing(
            expected_return_date=datetime.now() - timedelta(days=2),  # Минула дата
            actual_return_date=datetime.now(),
            is_active=False,
            user = user
        )

        url = reverse("borrowing:return_borrowing", args=[already_returned_borrowing.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_user_id(self):
        user1 = self.user
        user2 = get_user_model().objects.create_user(
            "test1@test.com",
            "testpass",
        )
        user3 = get_user_model().objects.create_user(
            "test2@test.com",
            "testpass",
        )
        borrowing1 = sample_borrowing(user=user1, is_active=True)
        borrowing2 = sample_borrowing(user=user2, is_active=True)

        borrowing3 = sample_borrowing(user=user3, is_active=False)

        res = self.client.get(
            BORROWINGS_URL, {"user_id": f"{user1.id},{user2.id}"}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_put_borrowing_not_allowed(self):
        book = sample_book()
        user = self.user
        payload = {
            "expected_return_date": "2029-09-20T15:39:57.710Z",
            "book": book.id,
        }

        borowwings = sample_borrowing(user=user)
        url = detail_url(borowwings.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        user = self.user
        borowwings = sample_borrowing(user=user)
        url = detail_url(borowwings.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
