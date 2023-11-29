from django.urls import path

from discord_messages.views import GetTelegramMessage, GetDiscordMessage

urlpatterns = [
    path("get-messages/", GetTelegramMessage.as_view(), name="get messages"),
    path("discord-webhook/", GetDiscordMessage.as_view(), name="message-webhook")
]
