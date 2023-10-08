from django.contrib import admin
from django.urls import path, include

from discord_messages.views import IndexView

urlpatterns = [
    path('admin/', include('loginas.urls')),
    path('admin/', admin.site.urls),
    path("api/discord_messages/", include("discord_messages.urls")),
    path("auth/", include("users.auth_urls")),
    path("", include("users.urls")),
    path("", IndexView.as_view(), name="index"),
    path("api/users/", include("users.api_urls")),
    path("orders/", include("orders.urls")),
]
