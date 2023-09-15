from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings.models import Borrowing, Payment
from books.serializers import BooksSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict) -> Any:
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_inventory(attrs["book"].inventory, ValidationError)
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",

            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentsListSerializer(PaymentsSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BooksSerializer(many=False, read_only=True)
    payments = PaymentsListSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.StringRelatedField(many=False)
    payments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
            "payments",
        )


class PaymentsDetailSerializer(PaymentsSerializer):
    borrowing = BorrowingDetailSerializer(many=False, read_only=True)
    book = BooksSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "book",
            "session_url",
            "session_id",
            "money_to_pay",
        )
