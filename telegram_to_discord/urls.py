from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from courses.views import PaymentsPageView
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
    path("courses/", include("courses.urls")),
    path("stable/", include("stable_messages.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("payments-page/", PaymentsPageView.as_view(), name="payments"),
    path(
        "alternative-payments/",
        TemplateView.as_view(template_name="alternative_payment_methods.html"),
        name="alternative_payments"
    ),
    path("support/", include("support.urls")),
    path("comments/", include("comments.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

handler404 = TemplateView.as_view(template_name="error.html")
handler500 = TemplateView.as_view(template_name="error.html")


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
