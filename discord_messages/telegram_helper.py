import random
import logging
import telebot
from django.conf import settings
from telebot import types

from discord_messages.models import ConfirmMessage
from users.models import User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)


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
        try:
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
        except Exception as e:
            logger.warning(f"Ошибка регистрации пользователя, {username}, {str(e)}")
            bot.send_message(chat_id, "Пожалуйста, попробуйте еще раз или напишите админу")
            return
        bot.send_message(
            chat_id,
            "Привет) Наташа напишет, когда можно будет начинать веселье)"
            # (f"Привет ✌️ Для продолжения регистрации перейдите по ссылке: {settings.SITE_DOMAIN}"
            #  f"/auth/registration/{user.id}/")
        )


def handle_command(message):
    """
    Обработка команд бота
    :param message:
    :return:
    """
    message_text = message.get("text")
    chat_id = message.get("chat").get("id")
    username = message.get("from", {}).get("username")
    if message_text == "/help":
        bot.send_message(
            chat_id,
            f"""Для того, чтобы начать генерацию, просто вводите текст промпта\n
                Для того, чтобы поменять пароль, введите /newpassword новый пароль\n
                Личный кабинет: {settings.SITE_DOMAIN},\n
                Техподдержка: {settings.TECH_BOT_URL}
            """
        )
    if message_text.startswith("/preset"):
        preset = message_text.replace("/preset", "")
        if preset and preset != " ":
            user = User.objects.filter(username=username).first()
            if not preset.startswith(" "):
                preset = f" {preset}"
            try:
                user.preset = preset
                user.save()
            except Exception:
                bot.send_message(chat_id, "Некорректное значение")
                return
            bot.send_message(chat_id, f"Установлен новый суффикс: '{preset }'")


def add_four_pics_buttons(buttons: list, message_id: int):
    """
    Добавляем кнопки сообщению с 4 картинками
    :param buttons:
    :param message_id:
    :return:
    """
    refresh_item = types.InlineKeyboardButton(
        "Сгенерировать снова",
        callback_data=f"button_send_again&&{message_id}"
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
        "Вариации",
        callback_data=f"button_change&&{message_id}"
    )
    buttons.append(change_item)
    return buttons


def add_seed_pic_buttons(buttons: list, message_id: int):
    """
    добавляем кнопки картинке с полученным сидом
    :return:
    """
    buttons = []
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
