import logging
from http import HTTPStatus

import telebot
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from stable_messages.ban_list import BAN_LIST
from stable_messages.tasks import create_video_from_image
from stable_messages.helpers.video_bot_helper import handle_start_command_video_bot, handle_command_video_bot
from users.models import User


bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)
__all__ = (
    "GetTelegramCallbackForFireWorks",
)


class GetTelegramCallbackForFireWorks(APIView):
    def post(self, request):
        try:
            logger.warning("get message")
            message = request.data.get("message")
            if not message:
                return Response(HTTPStatus.OK)
            chat = message.get("chat", {})
            if not chat:
                return Response(HTTPStatus.OK)
            chat_id = message.get("chat", {}).get("id")
            if chat_id in BAN_LIST:
                return Response(HTTPStatus.OK)
            message_text = message.get("text") or message.get("caption")
            chat_username = message.get("chat", {}).get("username")
            if not chat_username:
                bot.send_message(
                    chat_id,
                    text="Пожалуйста, установите своему аккаунту username"
                )
                return Response(HTTPStatus.OK)
            if message_text == "/start":
                handle_start_command_video_bot(chat_id, chat_username)
                return Response(HTTPStatus.OK)
            user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
            if not user:
                logger.warning(f"Не найден пользователь(, user = {chat_username}")
                bot.send_message(
                    chat_id=chat_id,
                    text="<pre>Вы не зарегистрированы в приложении</pre>",
                    parse_mode="HTML"
                )
                return Response(HTTPStatus.OK)
            if message_text and message_text.startswith("/"):
                handle_command_video_bot(user, message_text)
                return Response(HTTPStatus.OK)
            photos = message.get("photo")
            if not photos:
                bot.send_message(
                    chat_id=chat_id,
                    text="<pre>Вы забыли приложить картинку :)</pre>",
                    parse_mode="HTML"
                )
                return Response(HTTPStatus.OK)
            if user.remain_video_messages > 0:
                user.remain_video_messages -= 1
                user.save()
                create_video_from_image.delay(chat_id, photos, chat_username, user.id, message_text)
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text="<pre>У Вас закончились генерации</pre>",
                    parse_mode="HTML"
                )
        except Exception as e:
            raise Warning(str(e))
        return Response(HTTPStatus.OK)
