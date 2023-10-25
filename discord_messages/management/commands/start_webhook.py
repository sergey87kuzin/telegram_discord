from django.conf import settings
from django.core.management.base import BaseCommand

from discord_messages.telegram_helper import bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/api/discord_messages/get-messages/"
        )
        if result:
            print("started")
        else:
            print("start error")
