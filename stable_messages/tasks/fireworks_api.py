import requests
from datetime import datetime

from celery import shared_task
from django.conf import settings

from stable_messages.models import StableMessage, StableSettings
from users.models import User


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
