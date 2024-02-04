from django.core.management.base import BaseCommand

from comments.views import comment_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        result = comment_bot.remove_webhook()
        if result:
            print("removed")
        else:
            print("remove error")
