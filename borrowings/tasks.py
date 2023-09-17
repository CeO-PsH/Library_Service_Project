from borrowings.models import Borrowing

from celery import shared_task
from datetime import date, timedelta
from borrowings.notification import send_to_telegram


@shared_task
def send_message_about_borrowing_books() -> None:
    tomorrow = date.today() + timedelta(days=2)
    borrowing_book = Borrowing.objects.filter(
        is_active=True, expected_return_date__lt=tomorrow
    )
    if len(borrowing_book) > 0:
        for book in borrowing_book:
            send_to_telegram(
                f"Title: {book.book.title},"
                f" expected return date: {book.expected_return_date},"
                f" Customer{book.user.id}"
            )
    else:
        send_to_telegram("No borrowings overdue today!")
