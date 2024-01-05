import json
from random import randint

import telebot
import requests
from celery import shared_task
from django.conf import settings
from django.urls import reverse_lazy
from telebot import types

from stable_messages.choices import StableMessageTypeChoices, ZOOM_SCALES, SCALES
from stable_messages.models import StableMessage, StableAccount, StableSettings
from users.models import User

stable_bot = telebot.TeleBot(settings.STABLE_TELEGRAM_TOKEN)


@shared_task
def send_upscale_to_stable(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    upscale_image_url = "https://stablediffusionapi.com/api/v5/super_resolution"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "key": stable_account.api_key,
        "url": stable_message.first_image,
        "scale": 4,
        "webhook": None,  # settings.SITE_DOMAIN + reverse_lazy("stable_messages:upscale-webhook"),
        "face_enhance": False
    })
    response = requests.post(url=upscale_image_url, headers=headers, data=data)
    if response_data := response.json():
        stable_message.stable_request_id = response_data.get("id")
        stable_message.single_image = response_data.get("output")
        stable_message.save()


def get_user_prompts(user_id, eng_text):
    user = User.objects.filter(id=user_id).first()
    if "--no " in eng_text:
        positive, negative = eng_text.split("--no ")
    else:
        positive = eng_text
        negative = ""
    if style := user.style:
        positive_prompt = style.positive_prompt.format(prompt=positive)
        negative_prompt = negative + style.negative_prompt
    else:
        stable_settings = StableSettings.get_solo()
        positive_prompt = positive + stable_settings.positive_prompt
        negative_prompt = negative + stable_settings.negative_prompt
    return positive_prompt, negative_prompt


@shared_task
def send_vary_to_stable(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    positive_prompt, negative_prompt = get_user_prompts(stable_message.user_id, text)
    seed = randint(0, 16000000)
    stable_message.seed = seed
    vary_image_url = "https://stablediffusionapi.com/api/v3/img2img"
    headers = {'Content-Type': 'application/json'}
    stable_settings = StableSettings.get_solo()
    data = json.dumps(
        {
            "key": stable_account.api_key,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "init_image": stable_message.first_image,
            "width": stable_message.width,
            "height": stable_message.height,
            "samples": "4",
            "num_inference_steps": stable_settings.vary_num_inference_steps or "31",
            "safety_checker": "yes",
            "enhance_prompt": "yes",
            "guidance_scale": stable_settings.vary_guidance_scale or 7.5,
            "strength": stable_settings.vary_strength or 0.7,
            "seed": seed,
            "base64": "no",
            "lora_model": stable_settings.lora_model,
            "lora_strength": stable_settings.lora_strength,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
            "track_id": stable_message.id
        }
    )

    response = requests.post(url=vary_image_url, headers=headers, data=data)
    if response_data := response.json():
        stable_message.stable_request_id = response_data.get("id")
        if response_data.get("status") == "success":
            stable_message.single_image = response_data.get("output")[0]
            stable_message.first_image = response_data.get("output")[0]
            stable_message.second_image = response_data.get("output")[1]
            stable_message.third_image = response_data.get("output")[2]
            stable_message.fourth_image = response_data.get("output")[3]
        elif response_data.get("status") == "processing":
            stable_message.single_image = response_data.get("output")
        stable_message.save()
        if response_data.get("status") == "error":
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка изменения")


def get_zoom_sizes(scale):
    result = (64, 64)
    return ZOOM_SCALES.get(scale) or result


@shared_task
def send_zoom_to_stable(created_message_id, direction):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    positive_prompt, negative_prompt = get_user_prompts(stable_message.user_id, text)
    zoom_image_url = "https://stablediffusionapi.com/api/v5/outpaint"
    headers = {
        'Content-Type': 'application/json'
    }
    scale = text.split("--ar ")[-1]
    width, height = get_zoom_sizes(scale)
    data = json.dumps({
        "key": stable_account.api_key,
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "image": stable_message.first_image,
        "width": stable_message.width,
        "height": stable_message.height,
        "strength": 0.9,
        "translation_factor": 0.1,
        "seed": stable_message.seed,
        # "height_translation_per_step": height,
        # "width_translation_per_step": width,
        "num_inference_steps": 31,
        "as_video": "no",
        "num_interpolation_steps": 51,
        "walk_type": [direction],
        "track_id": stable_message.id,
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
    })

    response = requests.post(url=zoom_image_url, headers=headers, data=data)
    if response_data := response.json():
        if response_data.get("status") == "error" or "error_id" in response_data:
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка отдаления")
            return
        stable_message.stable_request_id = response_data.get("id")
        if response_data.get("status") == "success":
            stable_message.single_image = response_data.get("output")[0]
        stable_message.save()


def add_buttons_to_message(message_id):
    buttons_data = (
        ("⬅️", f"button_move&&left&&{message_id}"),
        ("➡️", f"button_move&&right&&{message_id}"),
        ("⬆️", f"button_move&&up&&{message_id}"),
        ("⬇️", f"button_move&&down&&{message_id}"),
        ("🔍", f"button_zoom&&{message_id}"),
        ("4️⃣x", f"button_upscale&&{message_id}"),
        ("🔢", f"button_vary&&{message_id}"),
    )
    buttons_u_markup = types.InlineKeyboardMarkup()
    buttons_u_markup.row_width = 4
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
            initial_text=message.initial_text,
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
        single_image__icontains="."
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


def get_sizes(scale):
    result = ("1024", "1024")
    return SCALES.get(scale) or result


@shared_task
def handle_image_message(eng_text: str, chat_id: int, photos: list, chat_username: str, user_id: int):
    try:
        count = StableMessage.objects.all().count()
        photo_id = photos[1].get("file_id")
        file_info = stable_bot.get_file(photo_id)
        downloaded_file = stable_bot.download_file(file_info.file_path)
        extension = file_info.file_path.split(".")[-1]
        file_name = f"{chat_username}{count}.{extension}"
        with open(f"media/messages/{file_name}", 'wb') as new_file:
            new_file.write(downloaded_file)
        image_url = settings.SITE_DOMAIN + "/media/messages/" + file_name
    except Exception as e:
        stable_bot.send_message(chat_id, text="Ошибка обработки картинки")
        return
    scale = ""
    if "--ar " in eng_text:
        scale = eng_text.split("--ar ")[-1]
    width, height = get_sizes(scale)
    seed = randint(0, 16000000)
    created_message = StableMessage.objects.create(
        initial_text=eng_text,
        eng_text=eng_text,
        telegram_chat_id=chat_id,
        user_id=user_id,
        first_image=image_url,
        message_type=StableMessageTypeChoices.FIRST,
        width=width,
        height=height,
        seed=seed
    )
    created_message.refresh_from_db()
    send_vary_to_stable(created_message_id=created_message.id)


@shared_task
def check_not_sent_messages():
    not_sent_messages = StableMessage.objects.filter(
        stable_request_id__isnull=False,
        single_image__isnull=True,
        answer_sent=False
    )
    for message in not_sent_messages:
        fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{message.stable_request_id}"
        headers = {'Content-Type': 'application/json'}
        stable_account = StableAccount.objects.filter(stable_users__id=message.user_id).first()
        if not stable_account:
            return
        response = requests.post(url=fetch_url, headers=headers, data=json.dumps({"key": stable_account.api_key}))
        if response_data := response.json():
            if response_data.get("status") in ("error", "failed") or "error_id" in response_data:
                stable_bot.send_message(
                    chat_id=message.telegram_chat_id,
                    text=f"Ошибка генерации {message.initial_text}"
                )
                message.answer_sent = True
            if response_data.get("status") == "success":
                output = response_data.get("output")
                message.single_image = output[0]
                if len(output) > 1:
                    try:
                        message.first_image = output[0]
                        message.second_image = output[1]
                        message.third_image = output[2]
                        message.fourth_image = output[3]
                    except Exception:
                        pass
            message.save()


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
    message.width = width
    message.height = height
    message.seed = seed
    message.save()
    positive_prompt, negative_prompt = get_user_prompts(user_id, eng_text)
    text_message_url = "https://modelslab.com/api/v6/images/text2img"
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "key": stable_account.api_key,
        "model_id": stable_settings.model_id or "juggernaut-xl",
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "samples": "4",
        "num_inference_steps": stable_settings.num_inference_steps or "31",
        "seed": str(seed),
        "guidance_scale": stable_settings.guidance_scale or 7,
        "safety_checker": "no",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "yes",
        "upscale": "no",
        "lora_model": stable_settings.lora_model,
        "lora_strength": stable_settings.lora_strength,
        "sampling_method": stable_settings.sampling_method or "euler",
        "algorithm_type": stable_settings.algorithm_type or "",
        "scheduler": stable_settings.scheduler or "DPMSolverMultistepScheduler",
        "embeddings_model": stable_settings.embeddings_model or None,
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
        "track_id": message_id,
        "tomesd": "yes",
        "use_karras_sigmas": "yes",
        "vae": None,
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
            print("no images")
        message.save()
    else:
        stable_bot.send_message(chat_id=message.telegram_chat_id, text="Ошибка создания сообщения")