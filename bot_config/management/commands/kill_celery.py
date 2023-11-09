import os
import socket
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Killing celery worker and beat...")
        socket.getaddrinfo(socket.gethostname(), None)

        os.popen("~/telegram_discord/kill_celery.sh")
        print("Done")
