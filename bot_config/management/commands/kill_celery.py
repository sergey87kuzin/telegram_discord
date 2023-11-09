import os
import socket
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Killing celery worker and beat...")
        socket.getaddrinfo(socket.gethostname(), None)

        os.popen("/Users/sergeykuzin/dev/telegram_to_discord/kill_celery.sh")
        print("Done")
