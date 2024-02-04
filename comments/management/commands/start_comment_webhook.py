from django.conf import settings
from django.core.management.base import BaseCommand

from comments.views import comment_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = comment_bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/comments/telegram-callback/"
        )
        if result:
            print("started")
        else:
            print("start error")
