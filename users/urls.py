from django.urls import path

from users.views import Profile, UserChangePasswordView, UserRestorePasswordView, UserRestoreChangePasswordView

app_name = "users"

urlpatterns = [
    path("user/", Profile.as_view(), name="detail-profile"),
    path("user/password/", UserChangePasswordView.as_view(), name="change-password"),
    path(
        "user/restore/password/",
        UserRestorePasswordView.as_view(),
        name="users-restore-password",
    ),
    path(
        "user/restore-change/password/",
        UserRestoreChangePasswordView.as_view(),
        name="users-restore-change-password",
    ),
]
