from django.core.management.base import BaseCommand

from support.views import support_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = support_bot.remove_webhook()
        if result:
            print("removed")
        else:
            print("remove error")
