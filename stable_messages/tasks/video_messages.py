import json

import requests
from celery import shared_task
from django.conf import settings
from django.urls import reverse_lazy

from discord_messages.telegram_helper import bot as stable_bot
from stable_messages.models import VideoMessages, StableAccount
from stable_messages.tasks import get_user_prompts

model_ids = ["svd", "dark-sushi-mix-vid", "epicrealismnaturalsi-vid", "hellonijicute25d-vid"]


@shared_task
def send_video_messages_to_stable():
    """https://docs.modelslab.com/video-api/imgtovideo"""
    video_messages = VideoMessages.objects.filter(
        request_id__isnull=True,
        successfully_generated=False,
        variables__isnull=False,
    )[:20]
    video_url = "https://modelslab.com/api/v6/video/img2video"
    headers = {'Content-Type': 'application/json'}
    api_key = StableAccount.objects.first().api_key
    domain = settings.SITE_DOMAIN
    for video_message in video_messages:
        prompt, negative_prompt = get_user_prompts(video_message.user_id, video_message.prompt)
        guidance_scale, motion_bucket_id = video_message.variables.split(":")
        if int(video_message.width) > int(video_message.height):
            width, height = 1024, 576
        else:
            width, height = 576, 1024
        user = video_message.user
        data = json.dumps({
            "key": api_key,
            "model_id": "svd",
            "negative_prompt": negative_prompt,
            "prompt": prompt,
            "width": width,
            "height": height,
            "fps": 6,
            "num_frames": 25,  # max = 25
            "num_inference_steps": 25,  # max = 50
            "min_guidance_scale": guidance_scale,
            "max_guidance_scale": guidance_scale,
            "motion_bucket_id": motion_bucket_id,
            "noise_aug_strength": 0,
            "output_type": "mp4",
            "instant_response": True,
            "init_image": video_message.initial_image,
            "webhook": domain + reverse_lazy("stable_messages:video-webhook"),
            "track_id": video_message.id,
        })
        response = requests.post(url=video_url, headers=headers, data=data)
        if response_data := response.json():
            if response_data.get("status") not in ["error", "failed"]:
                video_message.request_id = response_data.get("id")
                video_message.save()
            else:
                video_message.is_sent = True
                user.remain_video_messages += 1
                video_message.save()
                user.save()
                stable_bot.send_message(
                    chat_id=user.chat_id,
                    text=f"<pre>Генерация видео по картинке с текстом {video_message.prompt} не удалась,"
                         f" вам добавлена одна генерация</pre>",
                    parse_mode="HTML"
                )


@shared_task
def fetch_stable_video_messages():
    """https://docs.modelslab.com/video-api/fetchvideo"""
    video_messages = VideoMessages.objects.filter(
        request_id__isnull=False,
        is_sent=False
    )[:20]
    headers = {'Content-Type': 'application/json'}
    api_key = StableAccount.objects.first().api_key
    data = json.dumps({"key": api_key})
    for video_message in video_messages:
        fetch_url = f"https://modelslab.com/api/v6/video/fetch/{video_message.request_id}"
        response = requests.post(url=fetch_url, headers=headers, data=data)
        if response_data := response.json():
            status = response_data.get("status")
            if status == "success":
                video_message.video = response_data.get("output")[0]
                video_message.successfully_generated = True
                video_message.is_sent = True
                video_message.save()
                stable_bot.send_message(
                    video_message.telegram_chat_id,
                    f"{video_message.variables or '1.8:127'}. Скачайте готовое видео тут: {video_message.video}"
                )
            if response_data.get("status") in ["error", "failed"]:
                user = video_message.user
                video_message.is_sent = True
                user.remain_video_messages += 1
                video_message.save()
                user.save()
                stable_bot.send_message(
                    chat_id=user.chat_id,
                    text=f"<pre>Генерация видео по картинке с текстом {video_message.prompt} не удалась,"
                         f" вам добавлена одна генерация</pre>",
                    parse_mode="HTML"
                )


@shared_task
def send_video_messages_to_telegram_workflow():
    for video_message in VideoMessages.objects.filter(is_sent=False, video__isnull=False):
        video_message.is_sent = True
        video_message.save()
        stable_bot.send_message(
            video_message.telegram_chat_id,
            f"{video_message.variables or '1.8:127'}. Скачайте готовое видео тут: {video_message.video}"
        )
