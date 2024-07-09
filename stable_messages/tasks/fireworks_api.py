from pathlib import Path

import requests
from datetime import timedelta

import telebot
from celery import shared_task
from django.conf import settings
from PIL import Image
from django.utils.timezone import now

from stable_messages.models import VideoMessages
from users.models import User


bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


@shared_task
def create_video_from_image(chat_id, photos, chat_username, user_id, message_text=None):
    user = User.objects.filter(id=user_id).first()
    now_time = now().strftime("%d-%m_%H:%M:%S")
    try:
        photo_id = photos[-1].get("file_id")
        file_info = bot.get_file(photo_id)
        downloaded_file = bot.download_file(file_info.file_path)
        extension = file_info.file_path.split(".")[-1]
        file_name = f"{chat_username}{now_time}.{extension}"
        with open(f"media/messages/{file_name}", 'wb') as new_file:
            new_file.write(downloaded_file)
    except Exception as e:
        user.remain_video_messages += 1
        user.save()
        bot.send_message(chat_id, text="<pre>Ошибка обработки изображения</pre>", parse_mode="HTML")
        return
    image = Image.open(f"./media/messages/{file_name}")
    width, height = image.size
    if width >= height:
        new_image = image.resize((1024, 576))
    else:
        new_image = image.resize((576, 1024))
    new_file_name = f"{chat_username}{now_time}_new.{extension}"
    new_image.save(f"./media/messages/{new_file_name}")
    image_url = settings.SITE_DOMAIN + "/media/messages/" + new_file_name
    created_message = VideoMessages.objects.create(
        initial_image=image_url,
        telegram_chat_id=chat_id,
        user_id=user_id,
        variables=message_text
    )
    cfg_scale = 1.8
    motion_bucket_id = 127
    if message_text and ":" in message_text:
        str_cfg_scale, str_motion_bucket_id = message_text.split(":")
        try:
            cfg_scale = round(float(str_cfg_scale), 1)
            motion_bucket_id = int(str_motion_bucket_id)
        except Exception:
            user.remain_video_messages += 1
            user.save()
            bot.send_message(chat_id, "<pre>Неверно указаны параметры видео</pre>", parse_mode="HTML")
            return
    response = requests.post(
        f"https://api.stability.ai/v2beta/image-to-video",
        headers={
            "authorization": f"Bearer {settings.FIREWORKS_API_KEY}"
        },
        files={
            "image": open(f"./media/messages/{new_file_name}", "rb")
        },
        data={
            "seed": 0,
            "cfg_scale": cfg_scale,
            "motion_bucket_id": motion_bucket_id
        },
    )
    if response.ok:
        created_message.request_id = response.json().get('id')
        created_message.successfully_generated = True
        created_message.save()
        bot.send_message(chat_id, "Изображение принято в генерацию")
    else:
        user.remain_video_messages += 1
        user.save()
        bot.send_message(chat_id, "<pre>Ошибка генерации видео. Пожалуйста, попробуйте позже</pre>", parse_mode="HTML")


@shared_task
def fetch_video():
    """
    Видео генерится не сразу, у него нет callback. Нужно запрашивать по id
    """
    for message in VideoMessages.objects.filter(
        successfully_generated=True,
        is_sent=False
    ):
        response = requests.request(
            "GET",
            f"https://api.stability.ai/v2beta/image-to-video/result/{message.request_id}",
            headers={
                'accept': "video/*",  # Use 'application/json' to receive base64 encoded JSON
                'authorization': f"Bearer {settings.FIREWORKS_API_KEY}"
            },
        )
        if response.status_code == 202:
            print("Generation in-progress, try again in 10 seconds.")
        elif response.status_code == 200:
            print("Generation complete!")
            now_time = now().strftime("%d-%m_%H:%M:%S")
            with open(f"./media/videos/video{message.user.username}-{now_time}.mp4", 'wb') as file:
                file.write(response.content)
                message.video = f"{settings.SITE_DOMAIN}/media/videos/video{message.user.username}-{now_time}.mp4"
                bot.send_message(message.telegram_chat_id, f"{message.variables or '1.8:127'}. Скачайте готовое видео тут: {message.video}")
                message.is_sent = True
                message.save()
        else:
            user = message.user
            user.remain_video_messages += 1
            user.save()
            message.successfully_generated = False
            message.save()
            bot.send_message(
                message.telegram_chat_id,
                text="К сожалению, генерация не удалась. Мы добавили вам генерацию взамен неуспешной"
            )


@shared_task
def clear_space():
    for video_message in VideoMessages.objects.filter(
        created_at__lte=now() - timedelta(hours=24)
    ):
        if video_message.video:
            video = Path(video_message.video.replace(settings.SITE_DOMAIN, "."))
            video.unlink(missing_ok=True)
        if video_message.initial_image:
            message = Path(video_message.initial_image.replace(settings.SITE_DOMAIN, "."))
            message.unlink(missing_ok=True)
            message = Path(video_message.initial_image.replace(settings.SITE_DOMAIN, ".").replace("_new", ""))
            message.unlink(missing_ok=True)
        video_message.delete()
