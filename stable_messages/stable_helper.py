import logging
import re
from datetime import timedelta

import requests
from deep_translator import GoogleTranslator
from django.utils.timezone import now
from telebot import types

from discord_messages.denied_words import check_words
from discord_messages.telegram_helper import bot as stable_bot
from discord_messages.telegram_helper import handle_start_message, handle_command, preset_handler, style_handler
from stable_messages.models import StableMessage
from .ban_list import BAN_LIST
from .choices import StableMessageTypeChoices, SCALES
from .tasks import send_upscale_to_stable, send_zoom_to_stable, send_vary_to_stable, handle_image_message, \
    send_message_to_stable, send_vary_to_stable_new
from users.models import User

logger = logging.getLogger(__name__)


def get_sizes(scale):
    result = ("1024", "1024")
    return SCALES.get(scale) or result


def add_buttons_to_u_message(created_message_id):
    BUTTONS = {
        "Zoom Out 1.5x": f"button_zoom_1.5x&&{created_message_id}",
        "Zoom Out 2x": f"button_zoom_2x&&{created_message_id}",
        "Upscale": f"button_upscale&&{created_message_id}",
        "Вариации": f"button_vary&&{created_message_id}"
    }
    buttons_markup = types.InlineKeyboardMarkup()
    buttons_markup.row_width = 1
    buttons = []
    for button_key, button_value in BUTTONS.items():
        item = types.InlineKeyboardButton(
            button_key,
            callback_data=button_value
        )
        buttons.append(item)
    buttons_markup.add(*buttons)
    return buttons_markup


def handle_u_button(message_text, chat_id):
    answer_text = "Увеличиваем"
    prefix, button_number, stable_message_id = message_text.split("&&")
    first_message = StableMessage.objects.filter(id=stable_message_id).first()
    if not first_message:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при увеличении((")
        return
    image_url = ""
    if "1" in button_number:
        image_url = first_message.first_image
    elif "2" in button_number:
        image_url = first_message.second_image
    elif "3" in button_number:
        image_url = first_message.third_image
    elif "4" in button_number:
        image_url = first_message.fourth_image
    if not image_url:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при увеличении((")
        return
    try:
        photo = requests.get(image_url)
        stable_bot.send_photo(chat_id=chat_id, photo=photo.content)
    except Exception:
        stable_bot.send_message(
            chat_id,
            text=f"<a href='{image_url}'>Скачайте увеличенное фото тут</a>",
            parse_mode="HTML"
        )
    created_message = StableMessage.objects.create(
        initial_text=first_message.eng_text,
        eng_text=message_text,
        telegram_chat_id=first_message.telegram_chat_id,
        user_id=first_message.user_id,
        single_image=image_url,
        width=first_message.width,
        height=first_message.height
    )
    buttons_markup = add_buttons_to_u_message(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text, reply_markup=buttons_markup)


def handle_upscale_button(message_text, chat_id):
    answer_text = "Делаем upscale. Это долго. Ждите"
    prefix, stable_message_id = message_text.split("&&")
    first_message = StableMessage.objects.filter(id=stable_message_id).first()
    if not first_message:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при увеличении((")
        return
    created_message = StableMessage.objects.create(
        initial_text=first_message.initial_text,
        eng_text=message_text,
        telegram_chat_id=first_message.telegram_chat_id,
        user_id=first_message.user_id,
        first_image=first_message.single_image,
        message_type=StableMessageTypeChoices.UPSCALED,
        sent_to_stable=False
    )
    created_message.refresh_from_db()
    send_upscale_to_stable.delay(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_zoom_button(message_text, chat_id, direction):
    answer_text = "Отдаляем"
    stable_message_id = message_text.split("&&")[-1]
    first_message = StableMessage.objects.filter(id=stable_message_id).first()
    if not first_message:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при отдалении((")
        return
    created_message = StableMessage.objects.create(
        initial_text=first_message.initial_text,
        eng_text=message_text,
        telegram_chat_id=first_message.telegram_chat_id,
        user_id=first_message.user_id,
        first_image=first_message.single_image,
        message_type=StableMessageTypeChoices.ZOOM,
        width=first_message.width,
        height=first_message.height,
        seed=first_message.seed,
        sent_to_stable=False
    )
    created_message.refresh_from_db()
    send_zoom_to_stable.delay(created_message.id, direction)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_vary_button(message_text, chat_id):
    answer_text = "Делаем вариации"
    prefix, stable_message_id = message_text.split("&&")
    first_message = StableMessage.objects.filter(id=stable_message_id).first()
    if not first_message:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при отдалении((")
        return
    new_endpoint = True in User.objects.filter(id=first_message.user_id).values_list("is_test_user", flat=True)
    created_message = StableMessage.objects.create(
        initial_text=first_message.initial_text,
        eng_text=message_text,
        telegram_chat_id=first_message.telegram_chat_id,
        user_id=first_message.user_id,
        first_image=first_message.single_image,
        message_type=StableMessageTypeChoices.VARY,
        width=first_message.width,
        height=first_message.height,
        seed=first_message.seed,
        new_endpoint=new_endpoint,
        sent_to_stable=False
    )
    created_message.refresh_from_db()
    if new_endpoint:
        send_vary_to_stable_new.delay(created_message.id)
    else:
        send_vary_to_stable.delay(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_repeat_button(message_text, chat_id):
    prefix, stable_message_id = message_text.split("&&")
    first_message = StableMessage.objects.filter(id=stable_message_id).first()
    if not first_message:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка при повторной генерации((")
        return
    user = first_message.user

    answer_text = first_message.initial_text
    width, height = first_message.width, first_message.height
    if user.preset and user.preset not in answer_text:
        width, height = get_sizes(user.preset.replace(" --ar ", ""))
    if "--ar" in answer_text:
        answer_text = answer_text.split("--ar ")[-1]
    created_message = StableMessage.objects.create(
        initial_text=answer_text,
        eng_text=answer_text,
        telegram_chat_id=first_message.telegram_chat_id,
        user_id=first_message.user_id,
        first_image=first_message.single_image,
        message_type=StableMessageTypeChoices.FIRST,
        width=width,
        height=height,
        seed=first_message.seed,
        sent_to_stable=False
    )
    created_message.refresh_from_db()
    send_message_to_stable.delay(first_message.user_id, answer_text, created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=f"Творим волшебство: {answer_text}")


def check_remains(eng_text, user, chat_id):
    if not eng_text.startswith("button_u&&"):
        if user.remain_messages == 0:
            if not user.date_of_payment or user.date_payment_expired < now():
                stable_bot.send_message(
                    chat_id=chat_id,
                    text="Пожалуйста, оплатите доступ к боту",
                )
                return False
        if user.remain_messages > 0:
            user.remain_messages -= 1
            user.save()
        elif user.remain_paid_messages > 0:
            user.remain_paid_messages -= 1
            user.save()
        else:
            stable_bot.send_message(
                chat_id=chat_id,
                text="У вас не осталось генераций",
            )
            return False
    return True


def handle_text_message(message: dict, translator):
    chat = message.get("chat", {})
    if not chat:
        return "", "", "", ""
    chat_id = message.get("chat", {}).get("id")
    if chat_id in BAN_LIST:
        return "", "", "", ""
    message_text = message.get("text") or message.get("caption")
    if not message_text:
        stable_bot.send_message(
            chat_id=chat_id,
            text="<pre>Вы отправили пустое сообщение</pre>",
            parse_mode="HTML"
        )
        return "", "", "", ""
    if message_text.startswith("/start"):
        start_data = message_text.split(" ")
        partner_id = None
        if start_data[0] == "/start" and len(start_data) == 2:
            partner_id = start_data[1]
        handle_start_message(message, partner_id)
        return "", "", "", ""
    if message_text.startswith("/"):
        handle_command(message)
        return "", "", "", ""
    message_text = message_text \
        .replace("—", "--").replace(" ::", "::").replace("  ", " ").replace("-- ", "--")
    if re.findall("::\S+", message_text):
        message_text = message_text.replace("::", ":: ")
    chat_username = message.get("chat", {}).get("username")
    if not message_text or not chat_username or not chat_id:
        logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
        stable_bot.send_message(
            chat_id=chat_id,
            text="<pre>Вы отправили пустое сообщение</pre>",
            parse_mode="HTML"
        )
        return "", "", "", ""
    eng_text = translator.translate(message_text)
    if not eng_text:
        logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
        stable_bot.send_message(
            chat_id=chat_id,
            text="<pre>Вы отправили пустое сообщение</pre>",
            parse_mode="HTML"
        )
        return "", "", "", ""
    wrong_words = check_words(eng_text)
    if wrong_words:
        stable_bot.send_message(
            chat_id=chat_id,
            text=f"<pre>❌Вы отправили запрещенные слова: {wrong_words}</pre>",
            parse_mode="HTML"
        )
        return "", "", "", ""
    eng_text = eng_text.replace("-- ", "--").replace("blonde girl", "girl, blonde hair")
    user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
    if not user:
        logger.warning(f"Не найден пользователь(, user = {chat_username}")
        stable_bot.send_message(
            chat_id=chat_id,
            text="<pre>Вы не зарегистрированы в приложении</pre>",
            parse_mode="HTML"
        )
        return "", "", "", ""
    if user.preset and user.preset not in message_text and user.preset not in eng_text:
        message_text = message_text + user.preset
        eng_text = eng_text + user.preset
    photos = message.get("photo")
    if photos:
        handle_image_message.delay(eng_text, chat_id, photos, chat_username, user.id)
        return "", "", "", ""
    return user, message_text, eng_text, chat_id


def handle_telegram_callback(message_data: dict):
    translator = GoogleTranslator(source='auto', target='en')
    answer_text = "Творим волшебство"
    message = message_data.get("message")
    if message:
        user, message_text, eng_text, chat_id = handle_text_message(message, translator)
    else:
        button_data = message_data.get("callback_query")
        if button_data:
            chat_id = button_data.get("from", {}).get("id")
            if chat_id in BAN_LIST:
                return "", "", ""
            message_text = button_data.get("data")
            if StableMessage.objects.filter(
                eng_text=message_text,
                created_at__gt=now() - timedelta(minutes=1)
            ).exists():
                stable_bot.send_message(chat_id=chat_id, text="Вы уже нажимали на эту кнопку)")
                return "", "", ""
            chat_username = button_data.get("from", {}).get("username")
            if message_text.startswith("preset&&"):
                preset_handler(chat_id, chat_username, message_text)
                return "", "", ""
            if message_text.startswith("style&&"):
                style_handler(chat_id, chat_username, message_text)
                return "", "", ""
            reply_markup = button_data.get("message").get("reply_markup")
            buttons_markup = types.InlineKeyboardMarkup()
            buttons_markup.row_width = len(reply_markup.get("inline_keyboard")[0])
            buttons = []
            for line in reply_markup.get("inline_keyboard"):
                for button in line:
                    if button.get("callback_data") == button_data.get("data"):
                        item = types.InlineKeyboardButton(
                            "✅",
                            callback_data=button.get("callback_data")
                        )
                    else:
                        item = types.InlineKeyboardButton(
                            button.get("text"),
                            callback_data=button.get("callback_data")
                        )
                    buttons.append(item)
            buttons_markup.add(*buttons)
            try:
                stable_bot.edit_message_reply_markup(
                    message_id=button_data.get("message").get("message_id"),
                    reply_markup=buttons_markup,
                    chat_id=chat_id
                )
            except Exception:
                pass
            if not message_text or not chat_username or not chat_id:
                logger.warning(f"Ошибка кнопки чата. {chat_id}, {chat_username}, {message_text}")
                stable_bot.send_message(chat_id=chat_id, text="С этой кнопкой что-то не так")
                return "", "", ""
            eng_text = message_text
            user = User.objects.filter(username__iexact=chat_username).first()
            if not user:
                logger.warning(f"Не найден пользователь(, user = {chat_username}")
                stable_bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
                return "", "", ""
            if not check_remains(eng_text, user, chat_id):
                return "", "", ""
            if message_text.startswith("button_upscale"):
                handle_upscale_button(message_text, chat_id)
                return "", "", ""
            elif message_text.startswith("button_zoom&&"):
                handle_zoom_button(message_text, chat_id, "back")
                return "", "", ""
            elif message_text.startswith("button_move"):
                direction = message_text.split("&&")[1]
                handle_zoom_button(message_text, chat_id, direction)
                return "", "", ""
            elif message_text.startswith("button_vary"):
                handle_vary_button(message_text, chat_id)
                return "", "", ""
            elif message_text.startswith("button_send_again&&"):
                handle_repeat_button(message_text, chat_id)
                return "", "", ""
        else:
            user = User.objects.first()
            stable_bot.send_message(
                chat_id=user.chat_id,
                text="Кто-то опять косячит :)",
            )
            return "", "", ""
    if not eng_text or not check_remains(eng_text, user, chat_id):
        return "", "", ""
    try:
        message_type = StableMessageTypeChoices.FIRST
        new_endpoint = False
        if user.is_test_user:
            # message_type = StableMessageTypeChoices.DOUBLE
            new_endpoint = True
        created_message = StableMessage.objects.create(
            initial_text=message_text,
            eng_text=eng_text,
            telegram_chat_id=chat_id,
            user=user,
            message_type=message_type,
            new_endpoint=new_endpoint,
            sent_to_stable=False,
        )
    except Exception:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка создания сообщения")
        return "", "", ""
    stable_bot.send_message(chat_id=chat_id, text=answer_text)
    return user, eng_text, created_message.id
