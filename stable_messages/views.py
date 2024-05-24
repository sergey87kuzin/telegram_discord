import logging
from http import HTTPStatus

import telebot
from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from stable_messages.models import StableMessage
from users.models import User
from .ban_list import BAN_LIST
from .choices import StableMessageTypeChoices
from .tasks import send_message_to_stable_1, send_message_to_stable_2, send_message_to_stable_3, \
    send_message_to_stable_4, send_message_to_stable_new, send_vary_to_stable_new, create_video_from_image
from stable_messages.stable_helper import handle_telegram_callback
from .video_bot_helper import handle_start_command_video_bot, handle_command_video_bot

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


class GetTelegramCallback(APIView):

    def post(self, request):
        logger.warning("get message")
        user, eng_text, message_id = handle_telegram_callback(request.data)
        if user and eng_text and message_id:
            if user.is_test_user:
                send_message_to_stable_new.apply_async([user.id, eng_text, message_id, "4"], queue="telegram")
                return Response(HTTPStatus.OK)
            # send_message_to_stable.delay(user.id, eng_text, message_id)
            if user.account.queue_number == 0:
                send_message_to_stable_1.apply_async([user.id, eng_text, message_id], queue="telegram1")
            elif user.account.queue_number == 1:
                send_message_to_stable_2.apply_async([user.id, eng_text, message_id], queue="telegram2")
            elif user.account.queue_number in (2, 5):
                send_message_to_stable_3.apply_async([user.id, eng_text, message_id], queue="telegram3")
            elif user.account.queue_number == 3:
                send_message_to_stable_4.apply_async([user.id, eng_text, message_id], queue="telegram4")
        return Response(HTTPStatus.OK)


class GetTelegramCallbackForFireWorks(APIView):
    def post(self, request):
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
        return Response(HTTPStatus.OK)


class GetStableCallback(APIView):

    def post(self, request):
        data = request.data
        images = data.get("output")
        message_id = data.get("track_id")
        if images and data.get("status") == "success":
            message = StableMessage.objects.filter(Q(id=message_id) | Q(stable_request_id=data.get("id"))).first()
            user = message.user
            if user.is_test_user and message.message_type == StableMessageTypeChoices.DOUBLE:
                message.first_image = images[0]
                message.message_type = StableMessageTypeChoices.FIRST
                message.save()
                message.refresh_from_db()
                send_vary_to_stable_new.apply_async([message.id], countdown=3)
                return Response(status=HTTPStatus.OK)
            message.single_image = images[0]
            try:
                message.first_image = images[0]
                message.second_image = images[1]
                message.third_image = images[2]
                message.fourth_image = images[3]
            except Exception:
                print("wrong one")
            message.save()
        if data.get("status") in ("error", "failed"):
            message = StableMessage.objects.filter(stable_request_id=data.get("id")).first()
            if message:
                bot.send_message(
                    chat_id=message.telegram_chat_id,
                    text=f"Ошибка генерации сообщения {message.initial_text}"
                )
                message.answer_sent = True
                message.save()
                user = message.user
                user.remain_messages += 1
                user.save()
                user.refresh_from_db()
        return Response(status=HTTPStatus.OK)


class GetStableUpscaleCallback(APIView):

    def post(self, request):
        data = request.data
        message = StableMessage.objects.filter(stable_request_id=data.get("id")).first()
        if message:
            message.single_image = data.get("output")
            if not data.get("status") == "success":
                bot.send_message(
                    chat_id=message.telegram_id,
                    text="Ошибка upscale картинки"
                )
        return Response(status=HTTPStatus.OK)
