import shlex
import subprocess
import time

from django.utils import autoreload
from django.core.management.base import BaseCommand


def restart_celery():
    cmd = "pkill celery"
    subprocess.call(shlex.split(cmd))
    time.sleep(3)
    cmd = "celery --app=telegram_to_discord worker -l info --logfile=celery.log -Q default -n default &"
    subprocess.call(shlex.split(cmd))
    time.sleep(3)
    cmd = "celery --app=telegram_to_discord beat -l info --logfile=celery_beat.log &"
    subprocess.call(shlex.split(cmd))
    time.sleep(3)
    cmd = "celery --broker=redis://redis:6379 -A telegram_to_discord " \
          "flower --address=web --port=5555 --url_prefix=flower &"
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Start celery worker with autoreload...")

        autoreload.run_with_reloader(restart_celery)
