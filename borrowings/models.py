from django.db import models
from rest_framework.exceptions import ValidationError

from Library_Service_Project import settings
from books.models import Books

class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now=True)
    expected_return_date = models.DateTimeField(auto_now=False)
    actual_return_date = models.DateTimeField(auto_now=False, blank=True, null=True)
    book = models.ForeignKey(Books, related_name="borrowings", on_delete=models.CASCADE)
    user =  models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True, null=False)

    class Meta:
        models.UniqueConstraint(
            fields=["borrow_date", "expected_return_date", "actual_return_date"],
            name="unique date"
        )

    @staticmethod
    def validate_inventory(inventory: int, error_to_raise):
        for inventory_attr_value, inventory_attr_name in [
            (inventory, "numbers"),
        ]:
            if inventory_attr_value <= 0:
                raise error_to_raise(
                    {
                        inventory_attr_name:
                            f" The {inventory_attr_name} of inventory items must be greater than 0."
                    }
                )

    def clean(self):
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
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Borrow date: {self.borrow_date}, Book: {self.book.title}, User: {self.user}"
