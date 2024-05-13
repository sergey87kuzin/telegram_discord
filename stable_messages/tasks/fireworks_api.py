import requests
from datetime import datetime

import telebot
from celery import shared_task
from django.conf import settings
from PIL import Image

from stable_messages.models import StableMessage, StableSettings, VideoMessages
from users.models import User


bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


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
def get_fireworks_generation(stable_message_id: int):

    message = StableMessage.objects.filter(id=stable_message_id).first()
    positive_prompt, negative_prompt = get_user_prompts(message.user_id, message.eng_text)

    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
        headers={
            "authorization": f"Bearer {settings.FIREWORKS_API_KEY}",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": positive_prompt,
            "output_format": "jpeg",
            "aspect_ratio": "16:9",
            "model": "sd3-turbo"
        },
    )

    if response.status_code == 200:
        file_name = f"/media/tmp/{datetime.now().strftime('%m-%d %H:%M:%S')}.jpeg"
        with open(f".{file_name}", 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))

    message.single_image = f"{settings.SITE_DOMAIN}{file_name}"
    message.first_image = f"{settings.SITE_DOMAIN}{file_name}"
    message.save()


@shared_task
def create_video_from_image(chat_id, photos, chat_username, user_id, message_text=None):
    try:
        count = VideoMessages.objects.all().count()
        photo_id = photos[-1].get("file_id")
        file_info = bot.get_file(photo_id)
        downloaded_file = bot.download_file(file_info.file_path)
        extension = file_info.file_path.split(".")[-1]
        file_name = f"{chat_username}{count}.{extension}"
        with open(f"media/messages/{file_name}", 'wb') as new_file:
            new_file.write(downloaded_file)
    except Exception as e:
        bot.send_message(chat_id, text="Ошибка обработки картинки")
        return
    image = Image.open(f"./media/messages/{file_name}")
    new_image = image.resize((1024, 576))
    new_file_name = f"{chat_username}{count}_new.{extension}"
    new_image.save(f"./media/messages/{new_file_name}")
    image_url = settings.SITE_DOMAIN + "/media/messages/" + new_file_name
    created_message = VideoMessages.objects.create(
        initial_image=image_url,
        telegram_chat_id=chat_id,
        user_id=user_id,
    )
    cfg_scale = 1.8
    motion_bucket_id = 127
    if message_text and ":" in message_text:
        str_cfg_scale, str_motion_bucket_id = message_text.split(":")
        try:
            cfg_scale = round(float(str_cfg_scale), 1)
            motion_bucket_id = int(str_motion_bucket_id)
        except Exception:
            bot.send_message(chat_id, "Неверно указаны параметры видео")
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
        bot.send_message(chat_id, "Картинка принята в генерацию")
    else:
        bot.send_message(chat_id, "Ошибка генерации видео. Пожалуйста, попробуйте позже")


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
            count = VideoMessages.objects.all().count()
            with open(f"./media/videos/video{message.id}.mp4", 'wb') as file:
                file.write(response.content)
                message.video = f"{settings.SITE_DOMAIN}/media/videos/video{message.id}.mp4"
                bot.send_message(message.telegram_chat_id, f"Скачайте сохраненное видео тут: {message.video}")
                message.is_sent = True
                message.save()
        else:
            raise Exception(str(response.json()))
