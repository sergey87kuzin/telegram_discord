from django.urls import path

from stable_messages.views import GetTelegramCallback, GetStableCallback, GetStableUpscaleCallback

app_name = "stable_messages"

urlpatterns = [
    path("telegram_webhook/", GetTelegramCallback.as_view(), name="telegram-webhook"),
    path("stable_webhook/", GetStableCallback.as_view(), name="stable-webhook"),
    path("upscale_webhook/", GetStableUpscaleCallback.as_view(), name="upscale-webhook")
]
