from django.urls import path, include
from rest_framework import routers


from borrowings.views import BorrowingListViewSet, return_borrowing

app_name = "borrowing"
router = routers.DefaultRouter()
router.register("", BorrowingListViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/return/", return_borrowing, name="return")
]