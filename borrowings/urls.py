from django.urls import path, include
from rest_framework import routers


from borrowings.views import BorrowingListViewSet, return_borrowing, PaymentsViewSet

app_name = "borrowing"
router = routers.DefaultRouter()
router.register("borrowing", BorrowingListViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/return/", return_borrowing, name="return")
]