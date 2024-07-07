from http import HTTPStatus

import telebot
from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from stable_messages.choices import StableMessageTypeChoices
from stable_messages.models import StableMessage, VideoMessages
from stable_messages.tasks import send_vary_to_stable_new
__all__ = (
    "GetStableCallback",
    "GetStableUpscaleCallback",
    "GetStableVideoCallback"
)


bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


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
        if data.get("status") in ("failed", "error"):
            try:
                bot.send_message(
                    chat_id=1792622682,
                    text=str(data)
                )
            except Exception:
                raise Warning("No admin message")
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
            message.save()
        return Response(status=HTTPStatus.OK)


class GetStableVideoCallback(APIView):

    def post(self, request):
        data = request.data
        message = VideoMessages.objects.filter(id=data.get("track_id")).first()
        if message:
            status = data.get("status")
            if status == "success":
                message.video = data.get("output")[0]
                message.successfully_generated = True
                message.save()
            if status == "processing":
                return Response(status=HTTPStatus.BAD_REQUEST)
            if status not in ["success", "processing"]:
                bot.send_message(
                    chat_id=message.telegram_id,
                    text="Ошибка визуализации картинки"
                )
        return Response(status=HTTPStatus.OK)
