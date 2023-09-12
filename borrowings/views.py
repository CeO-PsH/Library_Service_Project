from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer


class BorrowingListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,GenericViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingListSerializer
