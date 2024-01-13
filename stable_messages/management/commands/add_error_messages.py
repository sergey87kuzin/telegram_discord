from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from stable_messages.models import StableMessage
from stable_messages.stable_helper import stable_bot


class Command(BaseCommand):

    def handle(self, *args, **options):
        not_sent_messages = StableMessage.objects.filter(
            answer_sent=False,
            created_at__lte=timezone.now() - timedelta(hours=5)
        )[:100]
        for message in not_sent_messages:
            user = message.user
            user.remain_messages += 1
            user.save()
            message.answer_sent = True
            message.save()
            try:
                stable_bot.send_message(
                    chat_id=message.telegram_chat_id,
                    text=f"Нам не удалось сделать генерацию по запросу {message.initial_text}"
                )
                stable_bot.send_message(
                    chat_id=message.telegram_chat_id,
                    text="Поэтому мы добавили вам одну генерацию, чтобы вы могли попробовать снова)"
                )
            except Exception:
                pass
