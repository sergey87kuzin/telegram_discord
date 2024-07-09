import json
import time
from datetime import timedelta
from random import randint

import requests
from PIL import Image
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from telebot import types

from discord_messages.telegram_helper import bot as stable_bot
from stable_messages.choices import StableMessageTypeChoices, ZOOM_SCALES, SCALES
from stable_messages.models import StableMessage, StableAccount, StableSettings, VideoMessages, SetVideoVariables
from users.models import User


def get_user_prompts(user_id, eng_text):
    user = User.objects.filter(id=user_id).first()
    if "--no " in eng_text:
        positive, negative = eng_text.split("--no ", 1)
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


def add_buttons_to_message(message_id):
    buttons_data = (
        # ("⬅️", f"button_move&&left&&{message_id}"),
        # ("➡️", f"button_move&&right&&{message_id}"),
        # ("⬆️", f"button_move&&up&&{message_id}"),
        # ("⬇️", f"button_move&&down&&{message_id}"),
        # ("🔍", f"button_zoom&&{message_id}"),
        # ("4️⃣x", f"button_upscale&&{message_id}"),
        # ("🔢", f"button_vary&&{message_id}"),
        ("🎦", f"button_visualize&&{message_id}"),
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
            stable_bot.send_photo(
                chat_id=message.telegram_chat_id,
                photo=photo.content,
                caption=new_message.initial_text,
                reply_markup=buttons_u_markup
            )
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
        markup = add_buttons_to_message(new_message.id)
        try:
            photo = requests.get(image)
            stable_bot.send_photo(
                chat_id=message.telegram_chat_id,
                photo=photo.content,
                caption=f"Вариация: {message.initial_text}",
                reply_markup=markup
            )
        except Exception:
            stable_bot.send_message(
                message.telegram_chat_id,
                text=f"<a href='{image}'>Скачайте увеличенное фото тут</a>",
                parse_mode="HTML"
            )
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
def send_stable_messages_to_telegram(messages_ids: list[int]):
    time.sleep(0.2)
    messages_to_send = StableMessage.objects.filter(id__in=messages_ids)
    for message in messages_to_send:
        try:
            if message.message_type == StableMessageTypeChoices.FIRST:
                send_first_messages(message)
            elif message.message_type == StableMessageTypeChoices.UPSCALED:
                send_upscaled_message(message)
            elif message.message_type == StableMessageTypeChoices.VARY:
                send_varied_message(message)
            elif message.message_type == StableMessageTypeChoices.ZOOM:
                send_zoomed_message(message)
        except Exception:
            pass


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
def send_stable_messages_to_telegram_1(messages_ids: list[int]):
    send_stable_messages_to_telegram(messages_ids)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_2(messages_ids: list[int]):
    send_stable_messages_to_telegram(messages_ids)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_3(messages_ids: list[int]):
    send_stable_messages_to_telegram(messages_ids)


@shared_task(time_limit=360)
def send_stable_messages_to_telegram_4(messages_ids: list[int]):
    send_stable_messages_to_telegram(messages_ids)
    # send_stable_messages_robot()


def get_sizes(scale):
    result = ("1024", "1024")
    return SCALES.get(scale) or result


@shared_task
def send_stable_messages_to_telegram_workflow():
    messages_to_send = list(StableMessage.objects.filter(
        answer_sent=False,
        single_image__icontains=".",
    ).values_list("id", flat=True).distinct()[:80])
    messages_len = len(messages_to_send)
    if messages_len == 0:
        return
    send_stable_messages_to_telegram_1.delay(messages_to_send[:20])
    if messages_len >= 20:
        send_stable_messages_to_telegram_2.delay(messages_to_send[20:40])
        if messages_len >= 40:
            send_stable_messages_to_telegram_3.delay(messages_to_send[40:60])
            if messages_len >= 60:
                send_stable_messages_to_telegram_4.delay(messages_to_send[60:80])


@shared_task
def handle_image_message(eng_text: str, chat_id: int, photos: list, chat_username: str, user_id: int):
    user = User.objects.filter(id=user_id).first()
    if user.remain_video_messages <= 0:
        stable_bot.send_message(
            user.telegram_chat_id,
            text="У вас не осталось видео генераций"
        )
        return
    if "--ar " in eng_text:
        eng_text = eng_text.split("--ar ")[0]
    now_time = now().strftime("%d-%m_%H:%M:%S")
    try:
        photo_id = photos[-1].get("file_id")
        file_info = stable_bot.get_file(photo_id)
        downloaded_file = stable_bot.download_file(file_info.file_path)
        extension = file_info.file_path.split(".")[-1]
        file_name = f"{chat_username}{now_time}.{extension}"
        with open(f"media/messages/{file_name}", 'wb') as new_file:
            new_file.write(downloaded_file)
    except Exception as e:
        user.remain_video_messages += 1
        user.save()
        stable_bot.send_message(chat_id, text="<pre>Ошибка обработки изображения</pre>", parse_mode="HTML")
        return
    image = Image.open(f"./media/messages/{file_name}")
    width, height = image.size
    if width >= height:
        new_image = image.resize((1024, 576))
        width, height = 1024, 576
    else:
        new_image = image.resize((576, 1024))
        width, height = 576, 1024
    new_file_name = f"{chat_username}{now_time}_new.{extension}"
    new_image.save(f"./media/messages/{new_file_name}")
    image_url = settings.SITE_DOMAIN + "/media/messages/" + new_file_name

    video_message = VideoMessages.objects.create(
        telegram_chat_id=chat_id,
        user_id=user_id,
        initial_image=image_url,
        prompt=eng_text,
        width=width,
        height=height,
    )
    SetVideoVariables.objects.update_or_create(
        username=user.username,
        defaults={
            "username": user.username,
            "video_message": video_message,
            "is_set": False
        }
    )
    stable_bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, задайте параметры видео в формате С:М,"
             " где С от 0 до 10 с шагом 0.1,"
             " М от 1 до 255 с шагом 1."
             " Например 1.7:24"
    )


@shared_task
def check_not_sent_messages():
    not_sent_messages = StableMessage.objects.filter(
        stable_request_id__isnull=False,
        answer_sent=False
    ).filter(Q(single_image__isnull=True) | Q(single_image="") | Q(single_image="[]")).exclude(stable_request_id="")
    for message in not_sent_messages:
        fetch_url = f"https://stablediffusionapi.com/api/v3/fetch/{message.stable_request_id}"
        if message.new_endpoint:
            fetch_url = f"https://modelslab.com/api/v6/realtime/fetch/{message.stable_request_id}"
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
