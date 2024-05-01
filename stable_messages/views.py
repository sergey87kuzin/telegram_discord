import logging
from http import HTTPStatus

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.telegram_helper import bot
from stable_messages.models import StableMessage
from .choices import StableMessageTypeChoices
from .tasks import send_message_to_stable_1, send_message_to_stable_2, send_message_to_stable_3, \
    send_message_to_stable_4, send_message_to_stable_new, send_vary_to_stable_new, get_fireworks_generation
from stable_messages.stable_helper import handle_telegram_callback

logger = logging.getLogger(__name__)


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
        user, eng_text, message_id = handle_telegram_callback(request.data)
        if user and eng_text and message_id:
            get_fireworks_generation.delay(message_id)
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
