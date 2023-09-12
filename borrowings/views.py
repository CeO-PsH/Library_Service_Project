from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from books.models import Books
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingSerializer,
    BorrowingDetailSerializer,
)


class BorrowingListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingListSerializer



    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        book_get = self.request.data.get("book", None)
        book = Books.objects.get(id=book_get)
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)