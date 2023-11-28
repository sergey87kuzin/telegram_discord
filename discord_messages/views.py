import re
from http import HTTPStatus
import logging

from django.conf import settings
from django.utils.timezone import now
from django.views import generic
from deep_translator import GoogleTranslator
from rest_framework.response import Response
from rest_framework.views import APIView

from discord_messages.choices import DiscordTypes
from discord_messages.discord_helper import send_message_to_discord, DiscordHelper, \
    send_u_line_button_command_to_discord, get_message_seed, send_vary_strong_message, send_vary_soft_message
from discord_messages.models import Message, DiscordConnection, DiscordAccount
from discord_messages.telegram_helper import bot, handle_start_message, handle_command
from users.models import User


logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class GetTelegramMessage(APIView):

    def post(self, request):
        logger.warning("get message")
        message = request.data.get("message")
        translator = GoogleTranslator(source='auto', target='en')
        answer_text = "Творим волшебство"

        if message:
            message_text = message.get("text").replace("—", "--").replace(" ::", "::")
            if re.findall("::\S+", message_text):
                message_text.replace("::", ":: ")
            after_create_message_text = message_text
            if message_text == "/start":
                handle_start_message(message)
                return Response(HTTPStatus.OK)
            if message_text.startswith("/"):
                handle_command(message)
                return Response(HTTPStatus.OK)
            chat_username = message.get("chat", {}).get("username")
            chat_id = message.get("chat", {}).get("id")
            if not message_text or not chat_username or not chat_id:
                logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
                bot.send_message(chat_id=chat_id, text="Вы отправили пустое сообщение")
                return Response(HTTPStatus.BAD_REQUEST)
            eng_text = translator.translate(message_text)
            no_ar_text = eng_text.split(" --")[0]
            message_type = DiscordTypes.START_GEN
            user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
            if not user:
                logger.warning(f"Не найден пользователь(, user = {chat_username}")
                bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
                return Response(HTTPStatus.BAD_REQUEST)
        else:
            button_data = request.data.get("callback_query")
            if button_data:
                message_text = button_data.get("data")
                chat_username = button_data.get("from", {}).get("username")
                chat_id = button_data.get("from", {}).get("id")
                if not message_text or not chat_username or not chat_id:
                    logger.warning(f"Ошибка кнопки чата. {chat_id}, {chat_username}, {message_text}")
                    bot.send_message(chat_id=chat_id, text="С этой кнопкой что-то не так")
                    return Response(HTTPStatus.BAD_REQUEST)
                eng_text = message_text
                user = User.objects.filter(username__iexact=chat_username).first()
                if not user:
                    logger.warning(f"Не найден пользователь(, user = {chat_username}")
                    bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
                    return Response(HTTPStatus.BAD_REQUEST)
                first_message = Message.objects.filter(id=message_text.split("&&")[-1]).first()
                message_type = DiscordTypes.UPSCALED
                # переменная для определения типа сообщения после создания
                after_create_message_text = message_text
                if message_text.startswith("button_u&&"):
                    answer_text = "Увеличиваем"
                if message_text.startswith("button_zoom&&") or message_text.startswith("button_vary"):
                    message_text = first_message.text
                    answer_text = "Делаем вариации" if message_text.startswith("button_vary") else "Отдаляем"
                    message_type = DiscordTypes.START_GEN
                elif message_text.startswith("button_change&&"):
                    message_text = first_message.text
                    message_type = DiscordTypes.START_GEN
                elif message_text.startswith("button_send_again&&"):
                    message_text = first_message.eng_text
                    eng_text = first_message.eng_text
                    message_type = DiscordTypes.START_GEN
                else:
                    message_text = first_message.eng_text
                no_ar_text = first_message.no_ar_text
            else:
                user = User.objects.first()
                bot.send_message(
                    chat_id=user.chat_id,
                    text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
                )
                return Response(HTTPStatus.BAD_REQUEST)
        if not user.date_of_payment or user.date_payment_expired < now():
            bot.send_message(
                chat_id=chat_id,
                text="Пожалуйста, оплатите доступ к боту",
            )
            return Response(HTTPStatus.BAD_REQUEST)
        created_message = Message.objects.create(
            text=message_text,
            eng_text=eng_text,
            no_ar_text=no_ar_text,
            user_telegram=chat_username,
            telegram_id=chat_id,
            user=user,
            answer_type=message_type
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
                logger.warning(f"Не удалось отправить сообщение, {account.login}, {status}")
                return Response(HTTPStatus.OK)
        if after_create_message_text.startswith(("button_zoom&&", "button_vary")):
            created_message.eng_text = created_message.text
            created_message.no_ar_text = created_message.text.split(" --")[0]
            created_message.save()
        bot.send_message(chat_id=chat_id, text=answer_text)
        return Response(HTTPStatus.OK)

    def choose_action(self, account, connection, message_text):
        if message_text.startswith("button_u&&") or message_text.startswith("button_zoom&&"):
            logger.warning(f"button zoom info: {message_text}")
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[2]).first()
            if not message:
                logger.warning(f"Не нашлось сообщение, {message_text}")
            status = send_u_line_button_command_to_discord(
                account=account,
                connection=connection,
                button_key=button_data[1],
                message=message
            )
        elif message_text.startswith("button_change&&"):
            logger.warning(f"button change info: {message_text}")
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            if not message:
                logger.warning(f"Не нашлось сообщение, {message_text}")
            status = get_message_seed(account, connection, message)
        elif message_text.startswith("button_vary_strong&&"):
            logger.warning(f"button vary info: {message_text}")
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            if not message:
                logger.warning(f"Не нашлось сообщение, {message_text}")
            status = send_vary_strong_message(
                message=message, account=account, connection=connection
            )
        elif message_text.startswith("button_vary_soft&&"):
            logger.warning(f"button vary soft info: {message_text}")
            button_data = list(message_text.split("&&"))
            message = Message.objects.filter(id=button_data[-1]).first()
            if not message:
                logger.warning(f"Не нашлось сообщение, {message_text}")
            status = send_vary_soft_message(
                message=message, account=account, connection=connection
            )
        else:
            logger.warning(f"message info: {message_text}")
            status = send_message_to_discord(message_text, account, connection)
        return status
