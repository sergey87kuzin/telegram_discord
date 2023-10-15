from http import HTTPStatus

from django.conf import settings
from django.views import generic
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.discord_helper import send_message_to_discord, DiscordHelper, \
    send_u_line_button_command_to_discord, send_v_line_button_command_to_discord
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
        if message:
            message_text = message.get("text")
            if message_text == "/start":
                handle_start_message(message)
                return Response(HTTPStatus.OK)
            chat_username = message.get("chat").get("username")
            chat_id = message.get("chat").get("id")
        else:
            button_data = request.data.get("callback_query")
            if button_data:
                message_text = button_data.get("data")
                chat_username = button_data.get("from", {}).get("username")
                chat_id = button_data.get("from", {}).get("id")
            else:
                return HTTPStatus.OK
        Message.objects.create(
            text=message_text,
            user_telegram=chat_username,
            telegram_id=chat_id
        )
        user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
        account = DiscordAccount.objects.filter(users=user).first()
        connection = DiscordConnection.objects.filter(account=account).first()
        if not connection:
            connection = DiscordHelper().get_new_connection(account)
        status = self.choose_action(account, connection, message_text)
        if status != HTTPStatus.NO_CONTENT:
            connection = DiscordHelper().get_new_connection(account)
            status = self.choose_action(account, connection, message_text)
            if status != HTTPStatus.NO_CONTENT:
                bot.send_message(
                    chat_id=chat_id,
                    text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
                )
        bot.send_message(chat_id=chat_id, text="Творим волшебство")
        return Response(HTTPStatus.OK)

    def choose_action(self, account, connection, message_text):
        if message_text.startswith("button_u"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[2]).first()
            status = send_u_line_button_command_to_discord(
                account=account,
                connection=connection,
                button_key=button_data[1],
                message=message
            )
        elif message_text.startswith("button_v"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[2]).first()
            status = send_v_line_button_command_to_discord(
                account=account,
                connection=connection,
                button_key=button_data[1],
                message=message,
                new_text="some_text"
            )
        else:
            status = send_message_to_discord(message_text, account, connection)
        return status


class StartListenTelegram(APIView):
    def get(self, request):
        result = bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/api/discord_messages/get-messages/"
        )
        if result:
            return Response(HTTPStatus.OK)
        return Response(HTTPStatus.BAD_REQUEST)


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
