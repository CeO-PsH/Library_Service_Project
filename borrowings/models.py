from django.db import models

from Library_Service_Project import settings
from books.models import Books

class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now=True)
    expected_return_date = models.DateTimeField(auto_now=False)
    actual_return_date = models.DateTimeField(auto_now=True)
    book = models.ForeignKey(Books, related_name="borrowings", on_delete=models.CASCADE)
    user =  models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        models.UniqueConstraint(
            fields=["borrow_date", "expected_return_date", "actual_return_date"],
            name="unique date"
        )

    def __str__(self):
        return f"Borrow date: {self.borrow_date}, Book: {self.book.title}, User: {self.user}"