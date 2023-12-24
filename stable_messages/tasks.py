import json
from random import randint

import telebot
import requests
from celery import shared_task
from django.conf import settings
from django.urls import reverse_lazy
from telebot import types

from stable_messages.choices import StableMessageTypeChoices
from stable_messages.models import StableMessage, StableAccount

stable_bot = telebot.TeleBot(settings.STABLE_TELEGRAM_TOKEN)


@shared_task
def send_upscale_to_stable(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    upscale_image_url = "https://stablediffusionapi.com/api/v5/super_resolution"
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "key": stable_account.api_key,
        "url": stable_message.first_image,
        "scale": 4,
        "webhook": None,    # settings.SITE_DOMAIN + reverse_lazy("stable_messages:upscale-webhook"),
        "face_enhance": False
    })
    response = requests.post(url=upscale_image_url, headers=headers, data=data)
    if response_data := response.json():
        stable_message.stable_request_id = response_data.get("id")
        stable_message.single_image = response_data.get("output")
        stable_message.save()


@shared_task
def send_vary_to_stable(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    seed = randint(0, 16000000)
    stable_message.seed = seed
    vary_image_url = "https://stablediffusionapi.com/api/v3/img2img"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(
        {
            "key": stable_account.api_key,
            "prompt": text,
            "init_image": stable_message.first_image,
            "width": stable_message.width,
            "height": stable_message.height,
            "samples": "4",
            "num_inference_steps": "20",
            "safety_checker": "yes",
            "enhance_prompt": "yes",
            "guidance_scale": 7.5,
            "strength": 0.7,
            "seed": seed,
            "base64": "no",
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
            "track_id": stable_message.id
        }
    )

    response = requests.post(url=vary_image_url, headers=headers, data=data)
    if response_data := response.json():
        stable_message.stable_request_id = response_data.get("id")
        stable_message.single_image = response_data.get("output")
        stable_message.save()
        if response_data.get("status") == "error":
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка изменения")


@shared_task
def send_zoom_to_stable(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    zoom_image_url = "https://stablediffusionapi.com/api/v5/outpaint"
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "key": stable_account.api_key,
        "url": stable_message.first_image,
        "prompt": text,
        "image": stable_message.first_image,
        "width": stable_message.width,
        "height": stable_message.height,
        "seed": stable_message.seed,
        "height_translation_per_step": 64,
        "width_translation_per_step": 64,
        "num_inference_steps": 20,
        "as_video": "no",
        "num_interpolation_steps": 32,
        "walk_type": ["back", "back", "back", "back"],
        "track_id": stable_message.id,
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
    })

    response = requests.post(url=zoom_image_url, headers=headers, data=data)
    if response_data := response.json():
        if response_data.get("status") == "error":
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка отдаления")
            return
        stable_message.stable_request_id = response_data.get("id")
        stable_message.single_image = response_data.get("output")[0]
        stable_message.save()



def add_buttons_to_message(message_id):
    buttons_data = (
        ("Zoom Out", f"button_zoom&&{message_id}"),
        ("Upscale", f"button_upscale&&{message_id}"),
        ("Вариации", f"button_vary&&{message_id}"),
    )
    buttons_u_markup = types.InlineKeyboardMarkup()
    buttons_u_markup.row_width = 1
    buttons = []
    for button in buttons_data:
        format_button = types.InlineKeyboardButton(
            button[0],
            callback_data=button[1]
        )
        buttons.append(format_button)
    buttons_u_markup.add(*buttons)
    return buttons_u_markup


def send_first_messages(message: StableMessage):
    images = {
        "U1": message.first_image,
        "U2": message.second_image,
        "U3": message.third_image,
        "U4": message.fourth_image
    }
    for button_name, image in images.items():
        if not image:
            continue
        new_message = StableMessage.objects.create(
            initial_text=message.eng_text,
            eng_text=f"button_u&&{button_name}&&{message.id}",
            telegram_chat_id=message.telegram_chat_id,
            user_id=message.user_id,
            single_image=image,
            answer_sent=True,
            message_type=StableMessageTypeChoices.U,
            width=message.width,
            height=message.height,
            seed=message.seed
        )
        new_message.refresh_from_db()
        buttons_u_markup = add_buttons_to_message(new_message.id)
        try:
            photo = requests.get(image)
            stable_bot.send_photo(chat_id=message.telegram_chat_id, photo=photo.content)
        except Exception:
            stable_bot.send_message(
                message.telegram_chat_id,
                text=f"<a href='{image}'>Скачайте увеличенное фото тут</a>",
                parse_mode="HTML"
            )
        stable_bot.send_message(message.telegram_chat_id, text=new_message.initial_text, reply_markup=buttons_u_markup)
    message.answer_sent = True
    message.save()


def send_upscaled_message(message: StableMessage):
    try:
        photo = requests.get(message.single_image)
        stable_bot.send_photo(chat_id=message.telegram_chat_id, photo=photo.content)
    except Exception:
        stable_bot.send_message(
            message.telegram_chat_id,
            text=f"<a href='{message.single_image}'>Скачайте увеличенное фото тут</a>",
            parse_mode="HTML"
        )
    stable_bot.send_message(
        chat_id=message.telegram_chat_id,
        text=f"🔍 {message.initial_text}"
    )
    message.answer_sent = True
    message.save()


def send_varied_message(message):
    images = {
        "V1": message.first_image,
        "V2": message.second_image,
        "V3": message.third_image,
        "V4": message.fourth_image
    }
    for button_name, image in images.items():
        if not image:
            continue
        new_message = StableMessage.objects.create(
            initial_text=message.eng_text,
            eng_text=f"button_u&&{button_name}&&{message.id}",
            telegram_chat_id=message.telegram_chat_id,
            user_id=message.user_id,
            single_image=image,
            answer_sent=True,
            message_type=StableMessageTypeChoices.U,
            width=message.width,
            height=message.height,
            seed=message.seed
        )
        new_message.refresh_from_db()
        try:
            photo = requests.get(image)
            stable_bot.send_photo(chat_id=message.telegram_chat_id, photo=photo.content)
        except Exception:
            stable_bot.send_message(
                message.telegram_chat_id,
                text=f"<a href='{image}'>Скачайте увеличенное фото тут</a>",
                parse_mode="HTML"
            )
        markup = add_buttons_to_message(message.id)
        stable_bot.send_message(
            chat_id=message.telegram_chat_id,
            text=f"Varied {message.initial_text}",
            reply_markup=markup
        )
    message.answer_sent = True
    message.save()


def send_zoomed_message(message):
    try:
        photo = requests.get(message.single_image)
        stable_bot.send_photo(chat_id=message.telegram_chat_id, photo=photo.content)
    except Exception:
        stable_bot.send_message(
            message.telegram_chat_id,
            text=f"<a href='{message.single_image}'>Скачайте отдаленное фото тут</a>",
            parse_mode="HTML"
        )
    markup = add_buttons_to_message(message.id)
    stable_bot.send_message(
        chat_id=message.telegram_chat_id,
        text=f"Zoomed {message.initial_text}",
        reply_markup=markup
    )
    message.answer_sent = True
    message.save()


@shared_task
def send_stable_messages_to_telegram():
    messages_to_send = StableMessage.objects.filter(
        answer_sent=False,
        single_image__isnull=False
    ).order_by("id").distinct("id")
    for message in messages_to_send:
        if message.message_type == StableMessageTypeChoices.FIRST:
            send_first_messages(message)
        elif message.message_type == StableMessageTypeChoices.UPSCALED:
            send_upscaled_message(message)
        elif message.message_type == StableMessageTypeChoices.VARY:
            send_varied_message(message)
        elif message.message_type == StableMessageTypeChoices.ZOOM:
            send_zoomed_message(message)
