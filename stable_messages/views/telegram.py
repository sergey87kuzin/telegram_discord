import logging
from http import HTTPStatus

from rest_framework.response import Response
from rest_framework.views import APIView

from stable_messages.helpers.stable_helper import handle_telegram_callback
__all__ = (
    "GetTelegramCallback",
)


logger = logging.getLogger(__name__)


class GetTelegramCallback(APIView):

    def post(self, request):
        logger.warning("get message")
        handle_telegram_callback(request.data)
        return Response(HTTPStatus.OK)
