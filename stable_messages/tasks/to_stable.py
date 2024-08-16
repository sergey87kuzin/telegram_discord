import json
from random import randint

import requests
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy

from discord_messages.telegram_helper import bot as stable_bot
from stable_messages.choices import StableMessageTypeChoices, ZOOM_SCALES, SCALES
from stable_messages.models import StableMessage, StableSettings, StableAccount
from stable_messages.tasks import get_user_prompts


def get_sizes(scale):
    result = ("1024", "1024")
    return SCALES.get(scale) or result


def send_message_to_stable(message, count: str = "4"):
    """https://docs.modelslab.com/image-generation/community-models/dreamboothtext2img"""
    stable_settings = StableSettings.get_solo()
    user_id = message.user_id
    eng_text = message.eng_text
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
        "samples": count,
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
        "instant_response": True,
        "algorithm_type": algorithm_type,
        "scheduler": scheduler,
        "embeddings_model": "vae-for-human" or embeddings_models,
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
        "track_id": message.id,
        "tomesd": "yes",
        "use_karras_sigmas": "yes",
        "vae": None,
    })

    response = requests.post(url=text_message_url, headers=headers, data=data)
    if response_data := response.json():
        if response_data.get("status") in ["success", "processing"]:
            message.stable_request_id = response_data.get("id")
            single_images = response_data.get("future_links")
            try:
                message.first_image = single_images[0]
                message.second_image = single_images[1]
                message.third_image = single_images[2]
                message.fourth_image = single_images[3]
            except Exception:
                print("no images")
        else:
            user = message.user
            user.remain_messages += 1
            user.save()
            message.answer_sent = True
            stable_bot.send_message(
                chat_id=user.telegram_chat_id,
                text=f"Генерация по запросу '{message.initial_text}' не удалась. Попробуйте снова"
            )
        message.sent_to_stable = True
        message.save()
    else:
        stable_bot.send_message(chat_id=message.telegram_chat_id, text="Ошибка создания сообщения")


def send_first_messages_to_stable(messages_ids):
    for message in StableMessage.objects.filter(id__in=messages_ids):
        send_message_to_stable(message)


@shared_task(time_limit=300)
def send_first_messages_to_stable_1(messages_ids):
    send_first_messages_to_stable(messages_ids)


@shared_task(time_limit=300)
def send_first_messages_to_stable_2(messages_ids):
    send_first_messages_to_stable(messages_ids)


@shared_task(time_limit=300)
def send_first_messages_to_stable_3(messages_ids):
    send_first_messages_to_stable(messages_ids)


@shared_task
def send_first_messages_to_stable_workflow():
    messages = list(StableMessage.objects.filter(
        message_type=StableMessageTypeChoices.FIRST,
        sent_to_stable=False,
        answer_sent=False
    ).values_list("id", flat=True)[:60])
    messages_len = len(messages)
    if messages_len == 0:
        return
    send_first_messages_to_stable_1.delay(messages[:20])
    if messages_len >= 20:
        send_first_messages_to_stable_2.delay(messages[20:40])
        if messages_len >= 40:
            send_first_messages_to_stable_3.delay(messages[40:60])


def send_upscale_to_stable(created_message_id):
    """https://docs.modelslab.com/image-editing/super-resolution"""
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
        "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:upscale-webhook"),
        "face_enhance": True
    })
    response = requests.post(url=upscale_image_url, headers=headers, data=data)
    if response_data := response.json():
        if response_data.get("status") in ["error", "failure"]:
            stable_message.is_sent = True
            stable_message.save()
            user = stable_message.user
            user.remain_messages += 1
            user.save()()
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка изменения")
            return
        stable_message.stable_request_id = response_data.get("id")
        stable_message.single_image = response_data.get("output")
        stable_message.save()


def send_vary_to_stable(created_message_id):
    """https://docs.modelslab.com/image-generation/community-models/dreamboothimg2img"""
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    positive_prompt, negative_prompt = get_user_prompts(stable_message.user_id, text)
    seed = randint(0, 16000000)
    stable_message.seed = seed

    stable_settings = StableSettings.get_solo()
    model_id = stable_settings.model_id or "juggernaut-xl"
    controlnet_model = stable_settings.controlnet_model
    controlnet_type = stable_settings.controlnet_type
    controlnet_conditioning_scale = stable_settings.controlnet_conditioning_scale
    num_inference_steps = stable_settings.vary_num_inference_steps or "31"
    guidance_scale = stable_settings.vary_guidance_scale or 7.5
    strength = stable_settings.vary_strength or 0.7
    lora_model = stable_settings.lora_model
    lora_strength = stable_settings.lora_strength
    scheduler = stable_settings.scheduler or "DPMSolverMultistepScheduler"
    if custom_settings := stable_message.user.custom_settings:
        model_id = custom_settings.model_id or model_id
        controlnet_model = custom_settings.controlnet_model or controlnet_model
        controlnet_type = custom_settings.controlnet_type or controlnet_type
        controlnet_conditioning_scale = custom_settings.controlnet_conditioning_scale or controlnet_conditioning_scale
        num_inference_steps = custom_settings.vary_num_inference_steps or num_inference_steps
        guidance_scale = custom_settings.vary_guidance_scale or guidance_scale
        strength = custom_settings.vary_strength or strength
        lora_model = custom_settings.lora_model or lora_model
        lora_strength = custom_settings.lora_strength or lora_strength
        scheduler = custom_settings.scheduler or scheduler

    # vary_image_url = "https://stablediffusionapi.com/api/v3/img2img"
    vary_image_url = "https://modelslab.com/api/v6/images/img2img"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(
        {
            "key": stable_account.api_key,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "model_id": model_id or "stable-diffusion-3-medium",
            "controlnet_model": controlnet_model,
            "controlnet_type": controlnet_type,
            "controlnet_conditioning_scale": controlnet_conditioning_scale,
            "init_image": stable_message.first_image,
            "control_image": stable_message.first_image,
            "mask_image": stable_message.first_image,
            "width": stable_message.width,
            "height": stable_message.height,
            "samples": "4",
            "num_inference_steps": 21,
            "safety_checker": "yes",
            "enhance_prompt": "no",
            "guidance_scale": guidance_scale,
            "strength": strength,
            "seed": seed,
            "base64": "no",
            "lora_model": lora_model,
            "lora_strength": lora_strength,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
            "track_id": stable_message.id,
            "scheduler": scheduler
        }
    )

    response = requests.post(url=vary_image_url, headers=headers, data=data)
    if response_data := response.json():
        stable_message.stable_request_id = response_data.get("id")
        stable_message.sent_to_stable = True
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
            stable_message.is_sent = True
            stable_message.save()
            user = stable_message.user
            user.remain_messages += 1
            user.save()()
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


@shared_task
def send_vary_to_stable_new(created_message_id):
    stable_message = StableMessage.objects.get(id=created_message_id)
    stable_account = StableAccount.objects.filter(stable_users__id=stable_message.user_id).first()
    if not stable_account:
        return
    text = stable_message.initial_text
    positive_prompt, negative_prompt = get_user_prompts(stable_message.user_id, text)
    seed = randint(0, 16000000)
    stable_message.seed = seed

    stable_settings = StableSettings.get_solo()
    strength = stable_settings.vary_strength or 0.7
    enhance_style = ""
    enhance_prompt = False
    if custom_settings := stable_message.user.custom_settings:
        strength = custom_settings.vary_strength or strength
        enhance_style = custom_settings.enhance_style
        enhance_prompt = True

    vary_image_url = "https://modelslab.com/api/v6/realtime/img2img"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(
        {
            "key": stable_account.api_key,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "init_image": stable_message.first_image,
            "width": stable_message.width,
            "height": stable_message.height,
            "samples": "4",
            "safety_checker": True,
            "enhance_prompt": enhance_prompt,
            "strength": strength,
            "seed": seed,
            "base64": False,
            "webhook": settings.SITE_DOMAIN + reverse_lazy("stable_messages:stable-webhook"),
            "track_id": stable_message.id,
            "enhance_style": enhance_style
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
            stable_message.first_image = response_data.get("future_links")[0]
            stable_message.second_image = response_data.get("future_links")[1]
            stable_message.third_image = response_data.get("future_links")[2]
            stable_message.fourth_image = response_data.get("future_links")[3]
        stable_message.save()
        if response_data.get("status") == "error":
            stable_bot.send_message(chat_id=stable_message.telegram_chat_id, text="Ошибка изменения")


@shared_task
def send_upscale_vary_messages_to_stable_workflow():
    not_sent_messages = StableMessage.objects.filter(
        answer_sent=False,
        sent_to_stable=False
    ).filter(Q(eng_text__startswith="button_vary") | Q(eng_text__startswith="button_upscale"))[:20]
    for message in not_sent_messages:
        if message.message_type == StableMessageTypeChoices.UPSCALED:
            send_upscale_to_stable(message.id)
        elif message.message_type == StableMessageTypeChoices.VARY:
            if message.new_endpoint:
                send_vary_to_stable_new(message.id)
            else:
                send_vary_to_stable(message.id)
