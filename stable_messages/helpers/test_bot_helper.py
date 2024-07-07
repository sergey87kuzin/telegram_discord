import json
import logging
import time
from random import randint
from typing import Union

import requests
import telebot
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy

from stable_messages.all_styles import all_styles, all_custom_styles
from stable_messages.choices import StableMessageTypeChoices
from stable_messages.models import TestMessage, StableAccount, StableSettings
from stable_messages.helpers.stable_helper import get_sizes
from users.models import User


test_bot = telebot.TeleBot(settings.STABLE_TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)


def make_request(url: str, data: str, message: TestMessage):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=url, headers=headers, data=data)
    if response_data := response.json():
        message.stable_request_id = response_data.get("id")
        if response_data.get("status") == "success":
            message.single_image = response_data.get("output")[0]
        elif response_data.get("status") in ("failed", "error"):
            message.answer_sent = True
            print("no data")
        message.save()


def handle_test_text_message(message: dict) -> tuple[
    Union[User, None],
    str,
    str,
]:
    chat = message.get("chat", {})
    if not chat:
        return None, "", ""
    chat_id = message.get("chat", {}).get("id")
    if str(chat_id) not in settings.ADMIN_CHAT_IDS:
        return None, "", ""
    message_text = message.get("text") or message.get("caption")
    if not message_text:
        test_bot.send_message(
            chat_id=chat_id,
            text="<pre>Кто-то забыл текст))</pre>",
            parse_mode="HTML"
        )
        return None, "", ""
    if message_text == "/start":
        test_bot.send_message(
            chat_id=chat_id,
            text="<pre>Привет, малыш) давай поиграем)</pre>",
            parse_mode="HTML"
        )
        return None, "", ""
    chat_username = message.get("chat", {}).get("username")
    if not chat_username or not chat_id:
        logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
        test_bot.send_message(
            chat_id=chat_id,
            text="<pre>С твоим профилем что-то не так)</pre>",
            parse_mode="HTML"
        )
        return None, "", ""
    user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
    if not user:
        logger.warning(f"Не найден пользователь(, user = {chat_username}")
        test_bot.send_message(
            chat_id=chat_id,
            text="<pre>пользователь куда-то подевался(</pre>",
            parse_mode="HTML"
        )
        return None, "", ""
    if user.preset and user.preset not in message_text:
        message_text = message_text + user.preset
    return user, message_text, chat_id


def handle_test_telegram_callback(data: dict) -> tuple[Union[User, None], Union[str, None]]:
    message = data.get("message")
    if message:
        user, message_text, chat_id = handle_test_text_message(message)
        return user, message_text
    return None, None


def handle_test_message_send(user: User, text: str) -> None:
    stable_account = StableAccount.objects.filter(stable_users=user.id).first()
    scale = ""
    if "--ar " in text:
        scale = text.split("--ar ")[-1]
    width, height = get_sizes(scale)
    seed = randint(0, 16000000)
    from stable_messages.tasks import get_user_prompts
    positive_prompt, negative_prompt = get_user_prompts(user.id, text)
    text_message_url = "https://modelslab.com/api/v6/realtime/text2img"
    api_key = stable_account.api_key
    for style in all_styles:
        time.sleep(5)
        created_message = TestMessage.objects.create(
            text=text,
            telegram_chat_id=user.chat_id,
            user=user,
            enhanced_style=style,
            width=width,
            height=height,
            seed=seed,
        )
        data = json.dumps({
            "key": api_key,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "samples": 1,
            "seed": str(seed),
            "enhance_prompt": True,
            "safety_checker": False,
            "instant_response": False,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:test-stable-webhook"),
            "track_id": created_message.id,
            "enhance_style": style,
        })
        make_request(text_message_url, data, created_message)


def handle_test_message_send_old(user: User, text: str) -> None:
    stable_account = StableAccount.objects.first()
    stable_settings = StableSettings.get_solo()
    if not stable_account:
        return

    scale = ""
    if "--ar " in text:
        scale = text.split("--ar ")[-1]
    width, height = get_sizes(scale)
    seed = randint(0, 16000000)

    model_id = "stable-diffusion-3-medium"
    num_inference_steps = stable_settings.num_inference_steps or "31"
    guidance_scale = stable_settings.guidance_scale or 7
    sampling_method = stable_settings.sampling_method or "euler"
    algorithm_type = stable_settings.algorithm_type or ""
    scheduler = stable_settings.scheduler or "DPMSolverMultistepScheduler"
    embeddings_models = stable_settings.embeddings_model or None
    if "--no " in text:
        positive, negative = text.split("--no ", 1)
    else:
        positive = text
        negative = ""
    for style in all_custom_styles:
        time.sleep(5)
        created_message = TestMessage.objects.create(
            text=text,
            telegram_chat_id=user.chat_id,
            user=user,
            enhanced_style=style[0],
            width=width,
            height=height,
            seed=seed,
        )
        if style[1]:
            positive_prompt = style[1].format(positive)
        else:
            positive_prompt = positive
        if style[2]:
            negative_prompt = negative + style[2]
        else:
            negative_prompt = ""
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
            "samples": 1,
            "num_inference_steps": num_inference_steps,
            # "seed": str(seed),
            "guidance_scale": guidance_scale,
            "enhance_prompt": "no",
            "safety_checker": "no",
            "panorama": "no",
            "self_attention": "no",
            "upscale": "no",
            "sampling_method": sampling_method,
            "algorithm_type": algorithm_type,
            "scheduler": scheduler,
            "embeddings_model": embeddings_models,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:test-stable-webhook"),
            "track_id": created_message.id,
            "tomesd": "yes",
            "use_karras_sigmas": "yes",
        })

        response = requests.post(url=text_message_url, headers=headers, data=data)
        if response_data := response.json():
            created_message.stable_request_id = response_data.get("id")
            single_images = response_data.get("future_links")
            try:
                created_message.first_image = single_images[0]
            except Exception:
                print("no images")
            created_message.save()
        else:
            test_bot.send_message(chat_id=created_message.telegram_chat_id, text="Ошибка создания сообщения")


def handle_test_bot_stable_message(message: TestMessage):
    pass


def send_image_to_video(message_id: int):
    stable_account = StableAccount.objects.first()
    message = TestMessage.objects.filter(id=message_id).first()
    if not message:
        return
    data = json.dumps({
        "key": stable_account.api_key,
        "model_id": "svd",
        "init_image": message.first_image,
        "height": message.height,
        "width": message.width,
        "num_frames": 25,
        "output_type": "mp4",
        "num_inference_steps": 20,
        "min_guidance_scale": 1,
        "max_guidance_scale": 3,
        "motion_bucket_id": 200,
        "noise_aug_strength": 0.02,
        "instant_response": True,
        "webhook": None,
        "track_id": None
    })
    video_message_url = "https://modelslab.com/api/v6/video/img2video"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url=video_message_url, headers=headers, data=data)
    if response_data := response.json():
        message.stable_request_id = response_data.get("id")
        single_images = response_data.get("future_links")
        try:
            message.single_image = single_images[0]
        except Exception:
            print("no images")
        message.save()
    else:
        test_bot.send_message(chat_id=message.telegram_chat_id, text="Ошибка создания видео")


def fetch_video(message_id: int):
    stable_account = StableAccount.objects.first()
    message = TestMessage.objects.filter(id=message_id).first()
    if not message:
        return
    fetch_video_url = f"https://modelslab.com/api/v6/video/fetch/{message.stable_request_id}"
    data = json.dumps({"key": stable_account.api_key})
    make_request(fetch_video_url, data, message)


def send_test_to_upscale(message_id: int):
    stable_account = StableAccount.objects.first()
    message = TestMessage.objects.filter(id=message_id).first()
    if not message:
        return
    upscale_image_url = "https://modelslab.com/api/v6/image_editing/super_resolution/"
    # upscale_image_url = "https://stablediffusionapi.com/api/v5/super_resolution"
    headers = {'Content-Type': 'application/json'}
    for style in [
        "RealESRGAN_x4plus",
        "RealESRNet_x4plus",
        "RealESRGAN_x4plus_anime_6B",
        "realesr-general-x4v3"
    ]:
        time.sleep(10)
        data = json.dumps({
            "key": stable_account.api_key,
            "url": message.single_image,
            "scale": 4,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:upscale-webhook"),
            "face_enhance": True,
            "model_id": style
        })
        new_message = TestMessage.objects.create(
            text=message.text,
            telegram_chat_id=message.telegram_chat_id,
            user=message.user,
            first_image=message.single_image,
            message_type=StableMessageTypeChoices.UPSCALED,
            enhanced_style=style
        )
        make_request(upscale_image_url, data, new_message)


def fetch_test_messages():
    stable_account = StableAccount.objects.first()
    not_sent_messages = (
        TestMessage.objects.filter(
            stable_request_id__isnull=False,
            answer_sent=False
        ).filter(Q(single_image__isnull=True) | Q(single_image="") | Q(single_image="[]"))
        .exclude(stable_request_id="")
    )
    fetch_url = f"https://modelslab.com/api/v6/images/fetch/"
    for message in not_sent_messages:
        data = json.dumps({
            "key": stable_account.api_key,
            "request_id": message.stable_request_id
        })
        fetch_url = f"https://modelslab.com/api/v6/image_editing/fetch/{message.stable_request_id}"
        # fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{message.stable_request_id}"
        make_request(fetch_url, data, message)


def make_zoom_test_image(message_id: int):
    stable_account = StableAccount.objects.first()
    message = TestMessage.objects.filter(id=message_id).first()
    if not message:
        return
    if "--no " in message.text:
        positive, negative = message.text.split("--no ", 1)
    else:
        positive = message.text
        negative = ""
    data = json.dumps({
        "key": stable_account.api_key,
        "seed": message.seed or None,
        "width": message.width or 512,
        "height": message.height or 512,
        "prompt": positive,
        "image": message.single_image,
        "negative_prompt": negative,
        "height_translation_per_step": 64,
        "width_translation_per_step": 64,
        "num_inference_steps": 15,
        "as_video": False,
        "num_interpolation_steps": 32,
        "walk_type": ["back", "back", "left", "left", "up", "up"],
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:upscale-webhook"),
        "track_id": message.id
    })
    zoom_url = "https://modelslab.com/api/v6/image_editing/outpaint/"
    make_request(zoom_url, data, message)
