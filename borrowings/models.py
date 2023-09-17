from typing import Any

from django.db import models
from rest_framework.exceptions import ValidationError

from Library_Service_Project import settings
from books.models import Books


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(
        blank=True,
        null=True
    )
    book = models.ForeignKey(
        Books,
        related_name="borrowings",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True, null=False)

    class Meta:
        models.UniqueConstraint(
            fields=[
                "borrow_date",
                "expected_return_date",
                "actual_return_date"
            ],
            name="unique date",
        )

    @staticmethod
    def validate_inventory(inventory: int, error_to_raise: Any) -> None:
        for inventory_attr_value, inventory_attr_name in [
            (inventory, "numbers"),
        ]:
            if inventory_attr_value <= 0:
                raise error_to_raise(
                    {
                        inventory_attr_name:
                            f" The {inventory_attr_name}"
                            f" of inventory items must be greater than 0."
                    }
                )

    def clean(self) -> None:
        Borrowing.validate_inventory(
            self.book.inventory,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ) -> None:
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return (
            f"Borrow date: {self.borrow_date},"
            f" Book: {self.book.title}, User: {self.user}"
        )


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING "
        PAID = "PAID"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(
        max_length=25, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(
        max_length=25,
        choices=Type.choices,
        default=Type.PAYMENT
    )
    borrowing = models.ForeignKey(
        Borrowing, related_name="payments", on_delete=models.CASCADE
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self) -> str:
        return (
            f"{self.id}.Status: {self.status},"
            f" Type:{self.type}, Money to pay: {self.money_to_pay} USD"
        )
