from datetime import datetime

from django.db import transaction
from django.db.models import F
from rest_framework import mixins, status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from books.models import Books
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingSerializer, BorrowingDetailSerializer,
)
from .send_messege_to_telegram import  send_to_telegram

class BorrowingListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = (IsAuthenticated, )

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        if self.request.user.is_staff:
            queryset = self.queryset
            user = self.request.query_params.get("user_id")
            if user:
                actors_ids = self._params_to_ints(user)
                queryset = queryset.filter(user__id__in=actors_ids)
        else:
            queryset = Borrowing.objects.filter(user=self.request.user)

        if is_active:
            return queryset.filter(is_active=is_active)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer


        return BorrowingSerializer

    def perform_create(self, serializer):
        data = self.request.data
        book = Books.objects.get(id=int(data['book']))
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)
        send_to_telegram(f"Borrowing №: {serializer.data['id']} Title: {book.title} Borrowing at:{datetime.now()}. Expected return date: {data['expected_return_date']}")

@api_view(["POST", "GET"])
def  return_borrowing(request: Request, pk) -> Response:
    with transaction.atomic():
        borrowing = get_object_or_404(Borrowing, id=pk)
        if borrowing.is_active:
            borrowing.book.inventory += 1
            borrowing.actual_return_date = datetime.now()
            borrowing.is_active = False
            borrowing.save()
            serializer = BorrowingDetailSerializer(borrowing)
            send_to_telegram(f"Borrowing №: {borrowing.id}, Title: {borrowing.book} was returned at: {borrowing.actual_return_date}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "The book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)