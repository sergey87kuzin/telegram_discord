from http import HTTPStatus

from django.views import generic
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.discord_helper import send_message_to_discord, DiscordHelper
from discord_messages.models import Message, DiscordConnection, DiscordAccount
from discord_messages.serializers import MessageSerializer
from discord_messages.telegram_helper import bot, handle_start_message
from users.models import User


class SendMessageToDiscord(GenericAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        return Response(status=HTTPStatus.OK, data=serializer.send_message())


class GetTelegramMessage(APIView):

    def post(self, request):
        message = request.data.get("message")
        message_text = message.get("text")
        if message_text == "/start":
            handle_start_message(message)
            return Response(HTTPStatus.OK)
        chat_username = message.get("chat").get("username")
        chat_id = message.get("chat").get("id")
        Message.objects.create(
            text=message_text,
            user_telegram=chat_username,
            telegram_id=chat_id
        )
        user = User.objects.filter(username=chat_username, is_active=True).first()
        account = DiscordAccount.objects.filter(users=user).first()
        connection = DiscordConnection.objects.filter(account=account).first()
        if not connection:
            connection = DiscordHelper().get_new_connection(user)
        status = send_message_to_discord(message_text, account, connection)
        if status != HTTPStatus.NO_CONTENT:
            connection = DiscordHelper().get_new_connection(user)
            status = send_message_to_discord(message_text, account, connection)
            if status != HTTPStatus.NO_CONTENT:
                bot.send_message(
                    chat_id=chat_id,
                    text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
                )
        bot.send_message(chat_id=chat_id, text="Творим волшебство")
        return Response(HTTPStatus.OK)


class StartListenTelegram(APIView):
    def get(self, request):
        result = bot.set_webhook(
            url="https://09d5-188-243-206-152.ngrok-free.app/api/discord_messages/get-messages/"
        )
        if result:
            return Response(HTTPStatus.OK)
        return Response(HTTPStatus.BAD_REQUEST)


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
