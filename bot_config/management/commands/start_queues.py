import os
import socket
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Starting queues...")
        socket.getaddrinfo(socket.gethostname(), None)

        os.popen("/Users/sergeykuzin/dev/telegram_to_discord/start_queues.sh")
        print("Done")
