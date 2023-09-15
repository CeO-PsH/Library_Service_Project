from datetime import timedelta, datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Books
from borrowings.models import Borrowing, Payment
from borrowings.serializers import PaymentsListSerializer, PaymentsDetailSerializer
from borrowings.views import create_checkout_session

PAYMENT_URL = reverse("borrowing:payment-list")

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
        "borrow_date": datetime.now(),
        "expected_return_date": datetime.now() + timedelta(days=2),
        "actual_return_date": datetime.now() + timedelta(days=5),
        "book": book,
        "is_active": True,
        "user": None,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)

def sample_payment(**params):

    defaults = {
        "status": "PENDING",
        "type": "PAYMENT",
        "borrowing": None,
        "session_url": "https://example.com/checkout",
        "session_id": "ID1234",
        "money_to_pay": 1000
    }
    defaults.update(params)

    return Payment.objects.create(**defaults)

def detail_url(payments_id):
    return reverse("borrowing:payment-detail", args=[payments_id])


class UnauthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_payment(self):
        res = self.client.get(PAYMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_payment(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        sample_payment(borrowing=borrowing)
        sample_payment(borrowing=borrowing)

        res = self.client.get(PAYMENT_URL)

        payment = Payment.objects.order_by("id")
        serializer = PaymentsListSerializer(payment, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


    def test_retrieve_payment_detail(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        payment = sample_payment(borrowing=borrowing)

        url = detail_url(payment.id)
        res = self.client.get(url)

        serializer = PaymentsDetailSerializer(payment)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_payment(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        payload = {
            "borrowing": borrowing.id,
            "session_url": "https://example.com/checkout",
            "session_id": "ID1234",
            "money_to_pay": 1000
        }
        res = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    @patch("borrowings.views.stripe.checkout.Session.create")
    def test_create_checkout_session_with_status_pending(self, mock_checkout_session):
        user = self.user
        borrowing = sample_borrowing(user=user)

        session_data = {
            "url": "https://example.com/checkout",
            "stripe_id": "stripe_session_id",
            "amount_total": Decimal(2000),
        }
        session_instance = type("Session", (object,), session_data)()
        mock_checkout_session.return_value = session_instance

        create_checkout_session(borrowing.pk, type_="PAYMENT")


        payment = Payment.objects.get(borrowing=borrowing)
        self.assertEqual(payment.session_url, "https://example.com/checkout")
        self.assertEqual(payment.session_id, "stripe_session_id")
        self.assertEqual(payment.type, "PAYMENT")
        self.assertEqual(payment.money_to_pay, Decimal(2000))


        mock_checkout_session.assert_called_once_with(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount_decimal": Decimal(2000),
                        "product_data": {
                            "name": borrowing.book.title,
                            "description": f"Author: {borrowing.book.author}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/api/borrowings/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/api/borrowings/canceled/",
        )

    @patch("borrowings.views.stripe.checkout.Session.create")
    def test_create_checkout_session_with_status_fine(self, mock_checkout_session):
        user = self.user
        borrowing = sample_borrowing(user=user)

        session_data = {
            "url": "https://example.com/checkout",
            "stripe_id": "stripe_session_id",
            "amount_total": Decimal(6000),
        }
        session_instance = type("Session", (object,), session_data)()
        mock_checkout_session.return_value = session_instance

        create_checkout_session(borrowing.pk, type_="FINE")
    

        payment = Payment.objects.get(borrowing=borrowing)
        self.assertEqual(payment.session_url, "https://example.com/checkout")
        self.assertEqual(payment.session_id, "stripe_session_id")
        self.assertEqual(payment.type, "FINE")
        self.assertEqual(payment.money_to_pay, Decimal(6000))
    

        mock_checkout_session.assert_called_once_with(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount_decimal": Decimal(6000),
                        "product_data": {
                            "name": borrowing.book.title,
                            "description": f"Author: {borrowing.book.author}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/api/borrowings/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/api/borrowings/canceled/",
        )

class AdminPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)


    def test_put_payment_not_allowed(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        payload = {
            "borrowing": borrowing.id,
            "session_url": "https://example.com/checkout",
            "session_id": "ID1234",
            "money_to_pay": 1000
        }

        payment = sample_borrowing(user=user)
        url = detail_url(payment.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_payment_not_allowed(self):
        user = self.user
        borrowing = sample_borrowing(user=user)
        payment = sample_payment(borrowing=borrowing)
        url = detail_url(payment.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
