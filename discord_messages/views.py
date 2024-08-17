# import re
import re
from http import HTTPStatus
import logging

from django.views import generic
from rest_framework.response import Response
from rest_framework.views import APIView
from discord_messages.tasks import send_message_to_discord_task, send_message_to_discord_task_1, \
    send_message_to_discord_task_2, send_message_to_discord_task_3
from discord_messages.telegram_helper import handle_message

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
        user_agent_key = request.META.get("HTTP_USER_AGENT")
        if user_agent_key and MOBILE_AGENT_RE.match(user_agent_key):
            context["is_mobile"] = True
        else:
            context["is_mobile"] = False
        return self.render_to_response(context)


class GetTelegramMessage(APIView):

    def post(self, request):
        logger.warning("get message")
        user, eng_text, chat_id = handle_message(request.data)
        # if user and eng_text and chat_id:
        #     if user.account.queue_number == 0:
        #         send_message_to_discord_task.apply_async([user.id, eng_text, chat_id], queue="messages")
        #     elif user.account.queue_number == 1:
        #         send_message_to_discord_task_1.apply_async([user.id, eng_text, chat_id], queue="messages1")
        #     elif user.account.queue_number == 2:
        #         send_message_to_discord_task_2.apply_async([user.id, eng_text, chat_id], queue="messages2")
        #     elif user.account.queue_number == 3:
        #         send_message_to_discord_task_3.apply_async([user.id, eng_text, chat_id], queue="messages3")
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
