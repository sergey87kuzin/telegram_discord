from django.conf import settings
from django.core.management.base import BaseCommand

from support.views import support_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = support_bot.set_webhook(
            url=f"{settings.SITE_DOMAIN}/support/telegram-callback/"
        )
        if result:
            print("started")
        else:
            print("start error")
