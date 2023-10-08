from django.conf import settings

from discord_messages.telegram_helper import send_confirm_code
from users.permissions import OnlyUnathorized
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.views import generic
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from users.models import User
from users.serializers import (
    AccountRestorePassword,
    AccountChangePasswordFromRestore,
    UserProfileSerializer,
)


class AccountRestoreView(generics.GenericAPIView):
    """
    Восстановление пароля
    """

    permission_classes = (OnlyUnathorized,)
    serializer_class = AccountRestorePassword

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=True)
        if is_valid:
            user = User.objects.filter(email=serializer.validated_data.get("email")).first()
            if user:
                send_confirm_code(user)
                return Response(
                    {"result": "Вам в бот отправлен код подтверждения"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Такого пользователя не зарегистрировано"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckRestoreToken(generic.View):
    """
    Проверка валидности кода восстановления
    """

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        code = kwargs.get("code")
        try:
            user = User.objects.get(pk=user_id, code=code)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user:
            return redirect(
                f"{settings.SITE_DOMAIN}"
                f"{reverse_lazy('users:user-restore-change-password')}"
                f"?uid={user_id}&restore_code={code}"
            )
        else:
            # todo: Добавить страницу неверной или истекшей ссылки.
            return HttpResponse("Activation link is invalid!")


class ChangePasswordCompleteView(generics.GenericAPIView):
    """
    Смена пароля при восстановлении аккаунта
    """

    permission_classes = (OnlyUnathorized,)
    serializer_class = AccountChangePasswordFromRestore

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.change_password()
        data = {
            "users": UserProfileSerializer(user, context=self.get_serializer_context()).data,
            "success": True,
        }
        return Response(data, status=status.HTTP_200_OK)
