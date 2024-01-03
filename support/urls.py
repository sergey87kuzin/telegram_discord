from django.urls import path

from support.views import SupportMessageAPIView

app_name = "support"

urlpatterns = [
    path("telegram-callback/", SupportMessageAPIView.as_view(), name="support_callback"),
]
