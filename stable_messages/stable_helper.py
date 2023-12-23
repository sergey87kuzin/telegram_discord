import json
import logging
import re
from random import randint

import requests
from deep_translator import GoogleTranslator
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now
from telebot import types

from discord_messages.denied_words import check_words
from discord_messages.telegram_helper import handle_start_message, handle_command, preset_handler
from stable_messages.models import StableMessage, StableAccount, StableSettings
from .choices import StableMessageTypeChoices, SCALES
from .tasks import send_upscale_to_stable, send_zoom_to_stable, stable_bot, send_vary_to_stable
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
    photo = requests.get(image_url)
    try:
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
        single_image=image_url
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
        message_type=StableMessageTypeChoices.UPSCALED
    )
    created_message.refresh_from_db()
    send_upscale_to_stable.delay(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_zoom_button(message_text, chat_id):
    answer_text = "Отдаляем"
    prefix, stable_message_id = message_text.split("&&")
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
        message_type=StableMessageTypeChoices.ZOOM
    )
    created_message.refresh_from_db()
    send_zoom_to_stable.delay(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_vary_button(message_text, chat_id):
    answer_text = "Вносим изменения"
    prefix, stable_message_id = message_text.split("&&")
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
        message_type=StableMessageTypeChoices.VARY
    )
    created_message.refresh_from_db()
    send_vary_to_stable.delay(created_message.id)
    stable_bot.send_message(chat_id=chat_id, text=answer_text)


def handle_repeat_button(message_text):
    pass


def handle_telegram_callback(message_data: dict):
    translator = GoogleTranslator(source='auto', target='en')
    answer_text = "Творим волшебство"
    message = message_data.get("message")
    if message:
        chat_id = message.get("chat", {}).get("id")
        message_text = message.get("text")
        if not message_text:
            stable_bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы отправили пустое сообщение</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        if message_text == "/start":
            handle_start_message(message)
            return "", "", ""
        if message_text.startswith("/"):
            handle_command(message)
            return "", "", ""
        message_text = message.get("text") \
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
            return "", "", ""
        eng_text = translator.translate(message_text)
        if not eng_text:
            logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
            stable_bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы отправили пустое сообщение</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        wrong_words = check_words(eng_text)
        if wrong_words:
            stable_bot.send_message(
                chat_id=chat_id,
                text=f"<pre>❌Вы отправили запрещенные слова: {wrong_words}</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        eng_text = eng_text.replace("-- ", "--")
        user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
        if not user:
            logger.warning(f"Не найден пользователь(, user = {chat_username}")
            stable_bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы не зарегистрированы в приложении</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        if user.preset and user.preset not in message_text and user.preset not in eng_text:
            message_text = message_text + user.preset
            eng_text = eng_text + user.preset
    else:
        button_data = message_data.get("callback_query")
        if button_data:
            chat_id = button_data.get("from", {}).get("id")
            message_text = button_data.get("data")
            if StableMessage.objects.filter(eng_text=message_text).exists():
                stable_bot.send_message(chat_id=chat_id, text="Вы уже нажимали на эту кнопку)")
                return "", "", ""
            chat_username = button_data.get("from", {}).get("username")
            if message_text.startswith("preset&&"):
                preset_handler(chat_id, chat_username, message_text)
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
            first_message = StableMessage.objects.filter(id=message_text.split("&&")[-1]).first()
            # if message_text.startswith("button_u&&"):
            #     handle_u_button(message_text, chat_id)
            #     return "", "", ""
            if message_text.startswith("button_upscale"):
                handle_upscale_button(message_text, chat_id)
                return "", "", ""
            elif message_text.startswith("button_zoom&&"):
                handle_zoom_button(message_text, chat_id)
                return "", "", ""
            elif message_text.startswith("button_vary"):
                handle_vary_button(message_text, chat_id)
                return "", "", ""
            elif message_text.startswith("button_send_again&&"):
                message_text = first_message.eng_text
                eng_text = first_message.eng_text
                handle_repeat_button(message_text)
                return "", "", ""
        else:
            user = User.objects.first()
            stable_bot.send_message(
                chat_id=user.chat_id,
                text="Кто-то опять косячит :)",
            )
            return "", "", ""
    if not eng_text.startswith("button_u&&"):
        if user.remain_messages == 0:
            if not user.date_of_payment or user.date_payment_expired < now():
                stable_bot.send_message(
                    chat_id=chat_id,
                    text="Пожалуйста, оплатите доступ к боту",
                )
                return "", "", ""
        if user.remain_paid_messages > 0:
            user.remain_paid_messages -= 1
            user.save()
        elif user.remain_messages > 0:
            user.remain_messages -= 1
            user.save()
        else:
            stable_bot.send_message(
                chat_id=chat_id,
                text="У вас не осталось генераций",
            )
            return "", "", ""
    try:
        created_message = StableMessage.objects.create(
            initial_text=message_text,
            eng_text=eng_text,
            telegram_chat_id=chat_id,
            user=user,
        )
    except Exception:
        stable_bot.send_message(chat_id=chat_id, text="Ошибка создания сообщения")
        return "", "", ""
    stable_bot.send_message(chat_id=chat_id, text=answer_text)
    return user, eng_text, created_message.id


def send_message_to_stable(user_id, eng_text, message_id):
    stable_settings = StableSettings.get_solo()
    message = StableMessage.objects.filter(id=message_id).first()
    stable_account = StableAccount.objects.filter(stable_users=user_id).first()
    if not stable_account:
        return
    scale = ""
    if "--ar " in eng_text:
        scale = eng_text.split("--ar ")[-1]
    width, height = get_sizes(scale)
    seed = randint(0, 16000000)
    text_message_url = "https://modelslab.com/api/v6/images/text2img"
    headers = {
        'Content-Type': 'application/json'
    }
    # todo выделять негативный промпт
    data = json.dumps({
        "key": stable_account.api_key,
        "model_id": stable_settings.model_id or "juggernaut-xl",
        "prompt": f"{stable_settings.positive_prompt}, {eng_text}",
        "negative_prompt": stable_settings.negative_prompt,
        "width": width,
        "height": height,
        "samples": "4",
        "num_inference_steps": stable_settings.num_inference_steps or "20",
        "seed": str(seed),
        "guidance_scale": stable_settings.guidance_scale or 7,
        "safety_checker": "yes",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "yes",
        "upscale": "no",
        "lora_model": "flat-illustration",
        "lora_strength": 0.5,
        "sampling_method": "euler",
        "algorithm_type": "",
        "scheduler": "DPMSolverMultistepScheduler",
        "embeddings_model": stable_settings.embeddings_model or None,
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
        "track_id": message_id
    })

    response = requests.post(url=text_message_url, headers=headers, data=data)
    if response_data := response.json():
        message.stable_request_id = response_data.get("id")
        single_images = response_data.get("future_links")
        try:
            message.first_image = single_images[0]
            message.second_image = single_images[1]
            message.third_image = single_images[2]
            message.fourth_image = single_images[3]
        except Exception:
            # todo решить, что делать, если фотки не пришли
            pass
        message.save()
    else:
        raise Warning("Не отправилось сообщение в stable")
