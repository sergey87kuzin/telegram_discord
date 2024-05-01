import telebot
from django.conf import settings
from django.core.management.base import BaseCommand

bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/stable/fireworks/telegram_webhook/"
        )
        if result:
            print("started")
        else:
            print("start error")
