import random
import telebot
from django.conf import settings

from discord_messages.models import ConfirmMessage
from users.models import User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def send_confirm_code(user: User):
    random_code = str(random.randint(0, 9999)).zfill(4)
    telegram_id = user.chat_id
    ConfirmMessage.objects.filter(telegram_nick=user.username).update(new_message_sent=True)
    ConfirmMessage.objects.create(
        telegram_nick=user.username,
        code=random_code
    )
    bot.send_message(chat_id=telegram_id, text=random_code)


def handle_start_message(message):
    username = message.get("from", {}).get("username")
    chat_id = message.get("chat").get("id")
    if username:
        user, created = User.objects.get_or_create(
            username__iexact=username,
            chat_id=chat_id,
            defaults={
                "username": username,
                "chat_id": chat_id,
            }
        )
        if created:
            user.set_password(str(random.randint(0, 99999999)).zfill(8))
            user.save()
    bot.send_message(
        chat_id,
        (f"Привет ✌️ Для продолжения регистрации перейдите по ссылке: {settings.SITE_DOMAIN}"
         f"/auth/registration/{user.id}/")
    )
