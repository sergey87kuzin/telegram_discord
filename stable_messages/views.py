import logging
from http import HTTPStatus

from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.telegram_helper import bot
from stable_messages.models import StableMessage
from .tasks import send_stable_messages_to_telegram
from stable_messages.stable_helper import send_message_to_stable, handle_telegram_callback

logger = logging.getLogger(__name__)


class GetTelegramCallback(APIView):

    def post(self, request):
        logger.warning("get message")
        user, eng_text, message_id = handle_telegram_callback(request.data)
        if user and eng_text and message_id:
            send_message_to_stable(user, eng_text, message_id)
        return Response(HTTPStatus.OK)


class GetStableCallback(APIView):

    def post(self, request):
        data = request.data
        images = data.get("output")
        message_id = data.get("track_id")
        if images:
            message = StableMessage.objects.filter(id=message_id).first()
            message.single_image = images[0]
            try:
                message.first_image = images[0]
                message.second_image = images[1]
                message.third_image = images[2]
                message.fourth_image = images[3]
            except Exception:
                pass
            message.save()
        if not data.get("status") == "success":
            message = StableMessage.objects.filter(stable_request_id=data.get("id")).first()
            if message:
                bot.send_message(
                    chat_id=message.telegram_id,
                    text="Ошибка генерации сообщения"
                )
        send_stable_messages_to_telegram.delay()
        Response(HTTPStatus.OK)


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
        Response(HTTPStatus.OK)
