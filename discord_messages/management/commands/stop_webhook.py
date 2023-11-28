from django.conf import settings
from django.core.management.base import BaseCommand

from discord_messages.telegram_helper import bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = bot.remove_webhook()
        if result:
            print("removed")
        else:
            print("remove error")
