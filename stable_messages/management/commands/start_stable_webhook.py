from django.conf import settings
from django.core.management.base import BaseCommand

from stable_messages.helpers.stable_helper import stable_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = stable_bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/stable/telegram_webhook/"
        )
        if result:
            print("started")
        else:
            print("start error")
