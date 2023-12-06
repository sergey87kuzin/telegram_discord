# import re
from http import HTTPStatus
import logging

# from django.conf import settings
# from django.utils.timezone import now
from django.views import generic
# from deep_translator import GoogleTranslator
from rest_framework.response import Response
from rest_framework.views import APIView
# from telebot import types
#
# from discord_messages.choices import DiscordTypes
# from discord_messages.discord_helper import send_message_to_discord, DiscordHelper, \
#     send_u_line_button_command_to_discord, get_message_seed, send_vary_strong_message, send_vary_soft_message
# from discord_messages.models import Message, DiscordConnection, DiscordAccount
# from discord_messages.telegram_helper import handle_message, bot, handle_start_message, handle_command, preset_handler
# from users.models import User
from discord_messages.tasks import send_message_to_discord_task
from discord_messages.telegram_helper import handle_message

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class GetTelegramMessage(APIView):

    def post(self, request):
        logger.warning("get message")
        user, eng_text, chat_id = handle_message(request.data)
        if user and eng_text and chat_id:
            send_message_to_discord_task.apply_async([user.id, eng_text, chat_id], queue="messages")
        return Response(HTTPStatus.OK)


class GetDiscordMessage(APIView):

    def post(self, request):
        data = request.data
        print("post", data)

        return Response(HTTPStatus.OK)

    def get(self, request):
        data = request.data
        print("get", data)

        return Response(HTTPStatus.OK)
