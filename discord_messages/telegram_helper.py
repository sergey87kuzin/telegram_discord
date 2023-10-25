import random
import telebot
from django.conf import settings
from telebot import types

from discord_messages.models import ConfirmMessage, Message
from users.models import User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def send_confirm_code(user: User):
    """
    Отправить код подтверждения для регистрации
    :param user:
    :return:
    """
    random_code = str(random.randint(0, 9999)).zfill(4)
    telegram_id = user.chat_id
    ConfirmMessage.objects.filter(telegram_nick=user.username).update(new_message_sent=True)
    ConfirmMessage.objects.create(
        telegram_nick=user.username,
        code=random_code
    )
    bot.send_message(chat_id=telegram_id, text=random_code)


def handle_start_message(message):
    """
    Обработка сообщения при старте бота
    :param message:
    :return:
    """
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
    bot.send_message(chat_id, "Пожалуйста, попробуйте еще раз")


def add_four_pics_buttons(buttons: list, eng_text: str):
    """
    Добавляем кнопки сообщению с 4 картинками
    :param buttons:
    :param eng_text:
    :return:
    """
    refresh_item = types.InlineKeyboardButton(
        "Сгенерировать снова",
        callback_data=eng_text
    )
    buttons.append(refresh_item)
    return buttons


def add_upscaled_pic_buttons(message_id: int, buttons: list):
    """
    Добавляем кнопки увеличенной одной картинке
    :param message_id:
    :param buttons:
    :return:
    """
    change_item = types.InlineKeyboardButton(
        "Хотите изменить?",
        callback_data=f"button_change&&{message_id}"
    )
    buttons.append(change_item)
    return buttons


def add_seed_pic_buttons(buttons: list, message_id: int):
    """
    добавляем кнопки картинке с полученным сидом
    :return:
    """
    strong_vary_item = types.InlineKeyboardButton(
        "Сильное изменение",
        callback_data=f"button_vary_strong&&{message_id}"
    )
    soft_vary_item = types.InlineKeyboardButton(
        "Слабое изменение",
        callback_data=f"button_vary_soft&&{message_id}"
    )
    buttons.append(strong_vary_item)
    buttons.append(soft_vary_item)
    return buttons
