from http import HTTPStatus

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.telegram_helper import send_confirm_code
from users.models import User


class SendConfirmCode(APIView):
    telegram = serializers.CharField()

    def post(self, request, *args, **kwargs):
        telegram = request.data.get("telegram")
        user = User.objects.filter(username__iexact=telegram).first()
        if not user:
            raise serializers.ValidationError({"telegram": "Вы не активировали бота"})
        send_confirm_code(user)
        return Response(status=HTTPStatus.OK)
