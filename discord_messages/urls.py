from django.urls import path

from discord_messages.views import SendMessageToDiscord, GetTelegramMessage, StartListenTelegram

urlpatterns = [
    path("send/", SendMessageToDiscord.as_view(), name="send message"),
    path("get-messages/", GetTelegramMessage.as_view(), name="get messages"),
    path("start-listening/", StartListenTelegram.as_view(), name="start listening")
]
