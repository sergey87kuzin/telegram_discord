from http import HTTPStatus

from django.conf import settings
from django.utils.timezone import now
from django.views import generic
from deep_translator import GoogleTranslator
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.discord_helper import send_message_to_discord, DiscordHelper, \
    send_u_line_button_command_to_discord, get_message_seed, send_vary_strong_message, send_vary_soft_message
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
        translator = GoogleTranslator(source='auto', target='en')

        if message:
            message_text = message.get("text")
            if message_text == "/start":
                handle_start_message(message)
                return Response(HTTPStatus.OK)
            chat_username = message.get("chat").get("username")
            chat_id = message.get("chat").get("id")
            eng_text = translator.translate(message_text)
            user = User.objects.filter(username__iexact=chat_username).first()
        else:
            button_data = request.data.get("callback_query")
            if button_data:
                message_text = button_data.get("data")
                chat_username = button_data.get("from", {}).get("username")
                chat_id = button_data.get("from", {}).get("id")
                eng_text = message_text
                user = User.objects.filter(username__iexact=chat_username).first()
                first_message = Message.objects.filter(id=message_text.split("&&")[-1]).first()
                message_text = first_message.eng_text
            else:
                return HTTPStatus.OK
        if not user.date_of_payment or user.date_payment_expired < now():
            bot.send_message(
                chat_id=chat_id,
                text="Пожалуйста, оплатите доступ к боту",
            )
            return Response(HTTPStatus.OK)
        Message.objects.create(
            text=message_text,
            eng_text=eng_text,
            user_telegram=chat_username,
            telegram_id=chat_id,
            user=user
        )
        account = DiscordAccount.objects.filter(users=user).first()
        connection = DiscordConnection.objects.filter(account=account).first()
        if not connection:
            connection = DiscordHelper().get_new_connection(account)
        status = self.choose_action(account, connection, eng_text)
        if status != HTTPStatus.NO_CONTENT:
            connection = DiscordHelper().get_new_connection(account)
            status = self.choose_action(account, connection, eng_text)
            if status != HTTPStatus.NO_CONTENT:
                bot.send_message(
                    chat_id=chat_id,
                    text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
                )
                return Response(HTTPStatus.OK)
        bot.send_message(chat_id=chat_id, text="Творим волшебство")
        return Response(HTTPStatus.OK)

    def choose_action(self, account, connection, message_text):
        if message_text.startswith("button_u&&"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[2]).first()
            status = send_u_line_button_command_to_discord(
                account=account,
                connection=connection,
                button_key=button_data[1],
                message=message
            )
        elif message_text.startswith("button_change&&"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            status = get_message_seed(account, connection, message)
        elif message_text.startswith("button_vary_strong&&"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            status = send_vary_strong_message(
                message=message, account=account, connection=connection
            )
        elif message_text.startswith("button_vary_soft&&"):
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            status = send_vary_soft_message(
                message=message, account=account, connection=connection
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
