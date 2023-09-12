from rest_framework import viewsets

from books.models import Books
from books.permissions import IsAdminOrReadOnly
from books.serializers import BooksSerializer


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    permission_classes = (IsAdminOrReadOnly, )
