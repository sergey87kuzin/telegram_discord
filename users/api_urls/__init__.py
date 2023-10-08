from django.urls import include, path

from users.api_views.confirm import SendConfirmCode

app_name = "api-users"

urlpatterns = [
    path("", include("users.api_urls.profile")),
    path("telegram/confirm/", SendConfirmCode.as_view(), name="send-confirm-code"),
]
