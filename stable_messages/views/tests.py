from http import HTTPStatus

import telebot
from django.conf import settings
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from stable_messages.models import TestMessage
from stable_messages.helpers.test_bot_helper import handle_test_telegram_callback, handle_test_message_send, \
    handle_test_bot_stable_message
__all__ = (
    "GetTestTelegramCallback",
    "GetTestStableCallback",
)

test_bot = telebot.TeleBot(settings.STABLE_TELEGRAM_TOKEN)


class GetTestTelegramCallback(APIView):

    def post(self, request):
        user, text = handle_test_telegram_callback(request.data)
        if user and text:
            try:
                handle_test_message_send(user, text)
            except Exception as e:
                print(str(e))
        return Response(HTTPStatus.OK)


class GetTestStableCallback(APIView):

    def post(self, request):
        data = request.data
        images = data.get("output")
        message_id = data.get("track_id")
        if images and data.get("status") == "success":
            message = TestMessage.objects.filter(Q(id=message_id) | Q(stable_request_id=data.get("id"))).first()
            # user = message.user
            message.single_image = images[0]
            message.save()
            handle_test_bot_stable_message(message)
        elif data.get("status") != "processing":
            try:
                test_bot.send_message(
                    chat_id=1792622682,
                    text=str(data)
                )
            except Exception:
                raise Warning("No admin message")
        return Response(status=HTTPStatus.OK)
