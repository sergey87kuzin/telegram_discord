import json
import time
from datetime import timedelta
from random import randint

import requests
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from telebot import types

from discord_messages.telegram_helper import bot as stable_bot
from stable_messages.choices import StableMessageTypeChoices, ZOOM_SCALES, SCALES
from stable_messages.models import StableMessage, StableAccount, StableSettings
from users.models import User


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
        negative_prompt = f"{negative} {style.negative_prompt}"
    elif custom_settings := user.custom_settings:
        positive_prompt = custom_settings.positive_prompt.format(prompt=positive)
        negative_prompt = f"{negative} {custom_settings.negative_prompt}"
    else:
        stable_settings = StableSettings.get_solo()
        positive_prompt = f"{positive} {stable_settings.positive_prompt}"
        negative_prompt = f"{negative} {stable_settings.negative_prompt}"
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

    stable_settings = StableSettings.get_solo()
    controlnet_model = stable_settings.controlnet_model
    controlnet_type = stable_settings.controlnet_type
    controlnet_conditioning_scale = stable_settings.controlnet_conditioning_scale
    num_inference_steps = stable_settings.vary_num_inference_steps or "31"
    guidance_scale = stable_settings.vary_guidance_scale or 7.5
    strength = stable_settings.vary_strength or 0.7
    lora_model = stable_settings.lora_model
    lora_strength = stable_settings.lora_strength
    if custom_settings := stable_message.user.custom_settings:
        controlnet_model = custom_settings.controlnet_model or controlnet_model
        controlnet_type = custom_settings.controlnet_type or controlnet_type
        controlnet_conditioning_scale = custom_settings.controlnet_conditioning_scale or controlnet_conditioning_scale
        num_inference_steps = custom_settings.vary_num_inference_steps or num_inference_steps
        guidance_scale = custom_settings.vary_guidance_scale or guidance_scale
        strength = custom_settings.vary_strength or strength
        lora_model = custom_settings.lora_model or lora_model
        lora_strength = custom_settings.lora_strength or lora_strength

    vary_image_url = "https://stablediffusionapi.com/api/v3/img2img"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(
        {
            "key": stable_account.api_key,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "controlnet_model": controlnet_model,
            "controlnet_type": controlnet_type,
            "controlnet_conditioning_scale": controlnet_conditioning_scale,
            "init_image": stable_message.first_image,
            "control_image": stable_message.first_image,
            "mask_image": stable_message.first_image,
            "width": stable_message.width,
            "height": stable_message.height,
            "samples": "4",
            "num_inference_steps": num_inference_steps,
            "safety_checker": "yes",
            "enhance_prompt": "no",
            "guidance_scale": guidance_scale,
            "strength": strength,
            "seed": seed,
            "base64": "no",
            "lora_model": lora_model,
            "lora_strength": lora_strength,
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
        # ("⬅️", f"button_move&&left&&{message_id}"),
        # ("➡️", f"button_move&&right&&{message_id}"),
        # ("⬆️", f"button_move&&up&&{message_id}"),
        # ("⬇️", f"button_move&&down&&{message_id}"),
        # ("🔍", f"button_zoom&&{message_id}"),
        ("4️⃣x", f"button_upscale&&{message_id}"),
        ("🔢", f"button_vary&&{message_id}"),
        ("🔄", f"button_send_again&&{message_id}")
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
    stable_bot.send_message(
        message.telegram_chat_id,
        text=f"<a href='{message.single_image}'>Скачайте увеличенное фото тут</a>",
        parse_mode="HTML"
    )
    stable_bot.send_message(
        chat_id=message.telegram_chat_id,
        text=f"4х: {message.initial_text}"
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
        markup = add_buttons_to_message(new_message.id)
        stable_bot.send_message(
            chat_id=message.telegram_chat_id,
            text=f"Вариация: {message.initial_text}",
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
        text=f"Отдаление: {message.initial_text}",
        reply_markup=markup
    )
    message.answer_sent = True
    message.save()


# @shared_task(time_limit=360)
def send_stable_messages_to_telegram(account_id: int):
    time.sleep(0.2)
    messages_to_send = StableMessage.objects.filter(
        answer_sent=False,
        single_image__icontains=".",
        user__account_id=account_id
    ).order_by("id").distinct("id")[:20]
    for message in messages_to_send:
        if message.message_type == StableMessageTypeChoices.FIRST:
            send_first_messages(message)
        elif message.message_type == StableMessageTypeChoices.UPSCALED:
            send_upscaled_message(message)
        elif message.message_type == StableMessageTypeChoices.VARY:
            send_varied_message(message)
        elif message.message_type == StableMessageTypeChoices.ZOOM:
            send_zoomed_message(message)


def send_stable_messages_robot():
    time.sleep(0.2)
    messages_to_send = StableMessage.objects.filter(
        answer_sent=False,
        single_image__icontains=".",
        user__account_id=5
    ).order_by("id").distinct("id")[:20]
    for message in messages_to_send:
        urls_in_answer = [message.initial_text, message.single_image]
        try:
            if message.second_image:
                urls_in_answer.append(message.second_image)
                urls_in_answer.append(message.third_image)
                urls_in_answer.append(message.fourth_image)
        except Exception:
            print("single_image")
        result_text = "\n".join(urls_in_answer)
        stable_bot.send_message(
            chat_id=message.telegram_chat_id,
            text=result_text,
            parse_mode="HTML"
        )
        message.answer_sent = True
        message.save()


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_1():
    send_stable_messages_to_telegram(account_id=1)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_2():
    send_stable_messages_to_telegram(account_id=2)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_3():
    send_stable_messages_to_telegram(account_id=3)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_4():
    send_stable_messages_to_telegram(account_id=4)
    send_stable_messages_robot()


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
        answer_sent=False
    ).filter(Q(single_image__isnull=True) | Q(single_image="")).exclude(stable_request_id="")
    for message in not_sent_messages:
        fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{message.stable_request_id}"
        headers = {'Content-Type': 'application/json'}
        stable_account = StableAccount.objects.filter(stable_users__id=message.user_id).first()
        if not stable_account:
            return
        response = requests.post(url=fetch_url, headers=headers, data=json.dumps({"key": stable_account.api_key}))
        if response_data := response.json():
            if response_data == {"message": ""}:
                user = message.user
                user.remain_messages += 1
                user.save()
                message.answer_sent = True
            if response_data.get("status") in ("error", "failed") or "error_id" in response_data:
                try:
                    stable_bot.send_message(
                        chat_id=message.telegram_chat_id,
                        text=f"<pre>❌Ошибка генерации\n✅ вам добавлена 1 генерация, отправьте запрос заново\n{message.initial_text}</pre>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                user = message.user
                user.remain_messages += 1
                user.save()
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


@shared_task
def send_message_to_stable(user_id, eng_text, message_id):
    stable_settings = StableSettings.get_solo()
    message = StableMessage.objects.filter(id=message_id).first()
    stable_account = StableAccount.objects.filter(stable_users=user_id).first()
    if not stable_account:
        return

    custom_settings = message.user.custom_settings
    model_id = stable_settings.model_id or "juggernaut-xl"
    num_inference_steps = stable_settings.num_inference_steps or "31"
    guidance_scale = stable_settings.guidance_scale or 7
    sampling_method = stable_settings.sampling_method or "euler"
    algorithm_type = stable_settings.algorithm_type or ""
    scheduler = stable_settings.scheduler or "DPMSolverMultistepScheduler"
    embeddings_models = stable_settings.embeddings_model or None
    lora_model = stable_settings.lora_model
    lora_strength = stable_settings.lora_strength
    if custom_settings:
        model_id = custom_settings.model_id or model_id
        num_inference_steps = custom_settings.num_inference_steps or num_inference_steps
        guidance_scale = custom_settings.guidance_scale or guidance_scale
        sampling_method = custom_settings.sampling_method or sampling_method
        algorithm_type = custom_settings.algorithm_type
        scheduler = custom_settings.scheduler or scheduler
        embeddings_models = custom_settings.embeddings_model or embeddings_models
        lora_model = custom_settings.lora_model or lora_model
        lora_strength = custom_settings.lora_strength or lora_strength

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
        "model_id": model_id,
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "samples": "4",
        "num_inference_steps": num_inference_steps,
        "seed": str(seed),
        "guidance_scale": guidance_scale,
        "enhance_prompt": "no",
        "safety_checker": "no",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "yes",
        "upscale": "no",
        "lora_model": lora_model,
        "lora_strength": lora_strength,
        "sampling_method": sampling_method,
        "algorithm_type": algorithm_type,
        "scheduler": scheduler,
        "embeddings_model": embeddings_models,
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


@shared_task
def send_message_to_stable_1(user_id, eng_text, message_id):
    send_message_to_stable(user_id, eng_text, message_id)


@shared_task
def send_message_to_stable_2(user_id, eng_text, message_id):
    send_message_to_stable(user_id, eng_text, message_id)


@shared_task
def send_message_to_stable_3(user_id, eng_text, message_id):
    send_message_to_stable(user_id, eng_text, message_id)


@shared_task
def send_message_to_stable_4(user_id, eng_text, message_id):
    send_message_to_stable(user_id, eng_text, message_id)


@shared_task
def resend_messages():
    not_sent_messages = StableMessage.objects.filter(
        eng_text__startswith="button_",
        answer_sent=False,
        created_at__lt=timezone.now() - timedelta(hours=1)
    ).filter(Q(stable_request_id="") | Q(stable_request_id__isnull=True))
    for message in not_sent_messages:
        if message.message_type == StableMessageTypeChoices.UPSCALED:
            send_upscale_to_stable(message.id)
        elif message.message_type == StableMessageTypeChoices.VARY:
            send_vary_to_stable(message.id)
