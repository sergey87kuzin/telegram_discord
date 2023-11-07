from django.urls import path

from discord_messages.views import GetTelegramMessage

urlpatterns = [
    path("get-messages/", GetTelegramMessage.as_view(), name="get messages"),
]
