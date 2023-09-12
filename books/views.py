
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from books.models import Books
from books.serializers import BooksSerializer


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAuthenticated, )
