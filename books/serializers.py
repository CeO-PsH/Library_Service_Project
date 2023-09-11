from rest_framework import serializers

from books.models import Books


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")