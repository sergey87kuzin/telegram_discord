from django.core.management.base import BaseCommand

from stable_messages.helpers.stable_helper import stable_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = stable_bot.remove_webhook()
        if result:
            print("removed")
        else:
            print("remove error")
