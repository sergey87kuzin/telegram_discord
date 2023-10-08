from django.urls import path

from users.auth_views import (
    LoginFormView,
    LogoutView,
    RegistrationCompleteView,
    UserRegistrationView,
    AjaxUserRegistrationView, AjaxLogin,
)

app_name = "auth"

urlpatterns = [
    path("login/", LoginFormView.as_view(), name="login"),
    path("ajax-login/", AjaxLogin.as_view(), name="ajax-login"),
    path("registration/<int:pk>/", UserRegistrationView.as_view(), name="registration"),
    path("registration-ajax/", AjaxUserRegistrationView.as_view(), name="registration-ajax"),
    path(
        "registration/complete/",
        RegistrationCompleteView.as_view(),
        name="registration-complete",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
