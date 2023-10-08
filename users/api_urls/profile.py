from django.urls import path

from users.api_views.profile import ChangePasswordView, UserProfileApiView, UserProfileUpdateAPIView
from users.api_views.restore_password import (
    AccountRestoreView,
    CheckRestoreToken,
    ChangePasswordCompleteView,
)

app_name = "profile"

urlpatterns = [
    path("profile/", UserProfileApiView.as_view(), name="profile"),
    path("profile/update/", UserProfileUpdateAPIView.as_view(), name="profile-update"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("account-restore/", AccountRestoreView.as_view(), name="account-restore"),
    path(
        "check/account-restore/<uidb64>/<token>/",
        CheckRestoreToken.as_view(),
        name="account-restore-check",
    ),
    path(
        "account-restore/done/",
        ChangePasswordCompleteView.as_view(),
        name="account-restore-done",
    ),
]
