from django.urls import path

from orders.views import CreateOrderView, SuccessPage, FailPage, NotificationView

app_name = "orders"

urlpatterns = [
    path("create/", CreateOrderView.as_view(), name="create"),
    path("success/", SuccessPage.as_view(), name="success"),
    path("fail/", FailPage.as_view(), name="fail"),
    path("notification/", NotificationView.as_view(), name="notification")
]
