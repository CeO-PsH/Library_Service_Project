from django.urls import path, include
from rest_framework import routers


from borrowings.views import (
    BorrowingListViewSet,
    return_borrowing,
    PaymentsViewSet,
    order_success,
    order_canceled,
    # create_checkout_session,
)

app_name = "borrowing"
router = routers.DefaultRouter()
router.register("borrowings", BorrowingListViewSet)
router.register("payments", PaymentsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/return/", return_borrowing, name="return"),
    path("success", order_success),
    path("canceled/", order_canceled),
]