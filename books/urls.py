from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from books.views import BooksViewSet

app_name = "books"
router = routers.DefaultRouter()
router.register("books", BooksViewSet)

urlpatterns = [path("", include(router.urls))]