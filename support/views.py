from http import HTTPStatus

import telebot
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from support.models import SupportMessage
from users.models import User

support_bot = telebot.TeleBot(settings.SUPPORT_TELEGRAM_TOKEN)


class SupportMessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        message = data.get("message")
        if not message:
            return Response(status=HTTPStatus.OK)
        chat = message.get("chat", {})
        if not chat:
            return Response(status=HTTPStatus.OK)
        chat_id = message.get("chat", {}).get("id")
        message_text = message.get("text") or message.get("caption")
        if not message_text:
            support_bot.send_message(chat_id=chat_id, text="Вы отправили пустое сообщение")
            return Response(status=HTTPStatus.OK)
        if message_text == "/start":
            return Response(status=HTTPStatus.OK)
        telegram_username = message.get("chat", {}).get("username")
        if not telegram_username:
            support_bot.send_message(chat_id=chat_id, text="Пожалуйста, заполните ник для вашего аккаунта telegram")
            return Response(status=HTTPStatus.OK)
        answer_to_id = None
        if reply := message.get("reply_to_message"):
            username = "SergeyAKuzin"
            if reply.get("text"):
                username = reply.get("text").split(":")[0]
            if reply.get("caption"):
                username = reply.get("caption").split(":")[0]
            user = User.objects.filter(username=username[1:]).first()
            if user:
                answer_to_id = user.chat_id
        photo_id = None
        if photos := message.get("photo"):
            photo_id = photos[-1].get("file_id")
        support_message = SupportMessage.objects.create(
            telegram_username=telegram_username,
            message_text=message_text,
            telegram_chat_id=chat_id,
            telegram_message_id=message.get("id"),
            answer_to_id=answer_to_id,
            image=photo_id
        )
        if str(chat_id) in settings.ADMIN_CHAT_IDS:
            if answer_to_id:
                support_bot.send_message(
                    chat_id=answer_to_id,
                    text=message_text
                )
                if photo_id:
                    support_bot.send_photo(chat_id=answer_to_id, photo=photo_id)
        else:
            for chat_id in settings.ADMIN_CHAT_IDS:
                support_bot.send_message(
                    chat_id=chat_id,
                    text=f"@{telegram_username}: {message_text}"
                )
                if photo_id:
                    support_bot.send_photo(chat_id=chat_id, photo=photo_id)
            support_message.answered = True
            support_message.save()
        return Response(status=HTTPStatus.OK)
