import requests
import telebot
from celery import shared_task
from django.conf import settings

from stable_messages.models import TestMessage


test_bot = telebot.TeleBot(settings.STABLE_TELEGRAM_TOKEN)


@shared_task
def send_test_messages():
    messages = TestMessage.objects.filter(
        stable_request_id__isnull=False,
        answer_sent=False,
        single_image__isnull=False,
    ).distinct()
    for message in messages:
        try:
            photo = requests.get(message.single_image)
            test_bot.send_photo(
                chat_id=message.telegram_chat_id,
                photo=photo.content,
                caption=f"{message.text} + {message.enhanced_style}",
            )
        except Exception:
            test_bot.send_message(
                message.telegram_chat_id,
                text=f"<a href='{message.single_image}'>Скачайте увеличенное фото тут</a>",
                parse_mode="HTML"
            )
            test_bot.send_message(message.telegram_chat_id, text=f"{message.text} + {message.enhanced_style}")
        message.answer_sent = True
        message.save()

