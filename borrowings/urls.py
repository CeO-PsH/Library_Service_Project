from django.urls import path, include
from rest_framework import routers


from borrowings.views import (
    BorrowingListViewSet,
    return_borrowing,
    PaymentsViewSet,
    order_success,
    order_canceled,
)

app_name = "borrowing"
router = routers.DefaultRouter()
router.register("/", BorrowingListViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [

    path("", include(router.urls)),
    path("<int:pk>/return_borrowing/", return_borrowing, name="return_borrowing"),
    path("success", order_success),
    path("canceled/", order_canceled),
]
