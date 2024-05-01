import telebot
from django.conf import settings
from django.core.management.base import BaseCommand

bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = bot.remove_webhook()
        if result:
            print("removed")
        else:
            print("remove error")
