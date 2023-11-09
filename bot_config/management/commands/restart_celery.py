import os
import socket
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Start celery worker with autoreload...")
        socket.getaddrinfo(socket.gethostname(), None)

        os.popen("~/telegram_discord/restart_celery.sh")
