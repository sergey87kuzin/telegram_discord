from http import HTTPStatus

import telebot
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from support.models import SupportMessage

support_bot = telebot.TeleBot(settings.SUPPORT_TELEGRAM_TOKEN)


class SupportMessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        message = data.get("message")
        chat_id = message.get("chat", {}).get("id")
        message_text = message.get("text")
        if message_text == "/start":
            return Response(status=HTTPStatus.OK)
        telegram_username = message.get("chat", {}).get("username")
        answer_to_id = None
        if reply := message.get("reply_to_message"):
            answer_to_id = reply.get("chat").get("id")
        support_message = SupportMessage.objects.create(
            telegram_username=telegram_username,
            message_text=message_text,
            telegram_chat_id=chat_id,
            telegram_message_id=message.get("id"),
            answer_to_id=answer_to_id
        )
        if str(chat_id) in settings.ADMIN_CHAT_IDS:
            if answer_to_id:
                support_bot.send_message(
                    chat_id=answer_to_id,
                    text=message_text
                )
        else:
            for chat_id in settings.ADMIN_CHAT_IDS:
                support_bot.send_message(
                    chat_id=chat_id,
                    text=message_text
                )
            support_message.answered = True
            support_message.save()
        return Response(status=HTTPStatus.OK)
