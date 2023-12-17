import logging
import time
from datetime import timedelta
from http import HTTPStatus

import requests
from celery import shared_task
from django.db.models import Q
from django.utils.timezone import now
from telebot import types

from discord_messages.choices import DiscordTypes
from discord_messages.discord_helper import DiscordHelper
from discord_messages.models import DiscordAccount, Message, DiscordConnection
from discord_messages.telegram_helper import bot, add_four_pics_buttons, add_upscaled_pic_buttons, add_seed_pic_buttons, \
    handle_message, choose_action

logger = logging.getLogger(__name__)


@shared_task
def handle_telegram_message(request_data):
    handle_message(request_data)


@shared_task
def send_message_to_discord_task(user_id, eng_text, chat_id):
    account = DiscordAccount.objects.filter(users__id=user_id).first()
    time.sleep(int(account.queue_delay))
    connection = DiscordConnection.objects.filter(account=account).first()
    if not connection:
        connection = DiscordHelper().get_new_connection(account)
    status = choose_action(account, connection, eng_text)
    if status != HTTPStatus.NO_CONTENT:
        connection = DiscordHelper().get_new_connection(account)
        status = choose_action(account, connection, eng_text)
        if status != HTTPStatus.NO_CONTENT:
            bot.send_message(
                chat_id=chat_id,
                text="<pre>Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру</pre>",
                parse_mode="HTML"
            )
            logger.warning(f"Не удалось отправить сообщение, {account.login}, {status}")


@shared_task
def send_message_to_discord_task_1(user_id, eng_text, chat_id):
    send_message_to_discord_task(user_id, eng_text, chat_id)


@shared_task
def send_message_to_discord_task_2(user_id, eng_text, chat_id):
    send_message_to_discord_task(user_id, eng_text, chat_id)


@shared_task
def send_message_to_discord_task_3(user_id, eng_text, chat_id):
    send_message_to_discord_task(user_id, eng_text, chat_id)


@shared_task
def get_discord_messages():
    """
    Получаем непрочитанные сообщения, определяем их тип(первоначальная генерация 4 картинок
    или увеличение одной(от этого зависят кнопки под картинкой))
    :return:
    """
    time.sleep(1)
    not_answered_messages = list(Message.objects.filter(
        Q(seed_send=False, seed__isnull=False) | Q(answer_sent=False)
    ).values_list("id", flat=True))
    not_answered_accounts = DiscordAccount.objects\
        .filter(users__messages__id__in=not_answered_messages)\
        .prefetch_related("connections").order_by("id").distinct()
    for account in not_answered_accounts:
        get_messages_url = f"https://discord.com/api/v9/channels/{account.channel_id}/messages"
        if account.last_message_id:
            get_messages_url += f"?after={account.last_message_id}&limit=100"
        connection = DiscordConnection.objects.filter(account=account).first()
        if not connection:
            connection = DiscordHelper().get_new_connection(account)
        headers = {"Authorization": connection.token}
        response = requests.get(get_messages_url, headers=headers)
        if not response.ok:
            connection = DiscordHelper().get_new_connection(account)
            headers = {"Authorization": connection.token}
            response = requests.get(get_messages_url, headers=headers)
        if response.ok and response.json():
            all_messages = True
            data = response.json()
            for discord_message in data:
                if Message.objects.filter(discord_message_id=discord_message.get("id")).exists():
                    continue
                attachments_urls = []
                content = discord_message.get("content")
                if "**" in content:
                    request_text = content.split("**")[1]
                    if "<https://s.mj.run/" in request_text:
                        request_text = request_text.split("> ", 1)[-1]
                    if "--seed" in request_text:
                        request_text = request_text.split(" --seed")[0]
                    if message_reference := discord_message.get("message_reference"):
                        telegram_message = Message.objects.filter(
                            discord_message_id=message_reference.get("message_id")
                        ).first()
                    else:
                        telegram_message = Message.objects.filter(
                                Q(eng_text__iexact=request_text)
                                | Q(text__iexact=request_text)
                                | Q(no_ar_text__iexact=request_text)
                        ).filter(answer_type=DiscordTypes.START_GEN).filter(
                            Q(seed_send=False, seed__isnull=False) | Q(answer_sent=False)
                        ).last()
                        if not telegram_message:
                            no_ar_request_text = request_text.split(" --")[0]
                            telegram_message = Message.objects.filter(
                                Q(eng_text__iexact=no_ar_request_text)
                                | Q(text__iexact=no_ar_request_text)
                                | Q(no_ar_text__iexact=no_ar_request_text)
                            ).filter(answer_type=DiscordTypes.START_GEN).last()
                    if telegram_message:
                        if not discord_message.get("components"):
                            all_messages = False
                            continue
                        if "** - Image #" in content:
                            button_number = content.split("** - Image #")[-1][0]
                            request_text = f"button_u&&U{button_number}&&{telegram_message.id}"
                            telegram_message = Message.objects.filter(eng_text__istartswith=request_text).last()
                            if not telegram_message:
                                logger.warning(f"Не нашлось сообщение от дискорда, {request_text}")
                                continue
                            telegram_message.answer_type = DiscordTypes.UPSCALED
                        elif "**seed**" in content:
                            message_data = content.split("**")
                            job = message_data[4][2:-1]
                            seed = message_data[-1]
                            telegram_message = Message.objects.filter(job=job).last()
                            if not telegram_message:
                                logger.warning(f"Не нашлось сообщение от дискорда, {request_text}")
                                continue
                            telegram_message.seed = seed
                            telegram_message.answer_type = DiscordTypes.GOT_SEED
                            telegram_message.answer_sent = True
                        elif "Zoom Out" in content or "Upscaled" in content:
                            telegram_message = Message.objects.filter(
                                Q(eng_text__iexact=request_text)
                                | Q(text__iexact=request_text)
                                | Q(no_ar_text__iexact=request_text)
                            ).filter(answer_type=DiscordTypes.START_GEN).filter(
                                Q(seed_send=False, seed__isnull=False) | Q(answer_sent=False)
                            ).last()
                            if not telegram_message:
                                no_ar_request_text = request_text.split(" --")[0]
                                telegram_message = Message.objects.filter(
                                    Q(eng_text__iexact=no_ar_request_text)
                                    | Q(text__iexact=no_ar_request_text)
                                    | Q(no_ar_text__iexact=no_ar_request_text)
                                ).filter(answer_type=DiscordTypes.START_GEN).last()
                        telegram_message.discord_message_id = discord_message.get("id")
                        for line in discord_message.get("components"):
                            for component in line.get("components"):
                                if label := component.get("label"):
                                    telegram_message.buttons[label] = {
                                        "custom_id": component.get("custom_id"),
                                        "type": component.get("type"),
                                        "label": label,
                                        "emoji": component.get("emoji")
                                    }
                        no_job = True
                        for value in telegram_message.buttons.values():
                            if no_job:
                                try:
                                    if custom_id := value.get("custom_id"):
                                        for part in custom_id.split("::"):
                                            if "-" in part:
                                                telegram_message.job = part
                                except Exception:
                                    continue
                        for attachment in discord_message.get("attachments"):
                            attachments_urls.append(attachment.get("proxy_url").split("?")[0])
                        telegram_message.images = ", ".join(attachments_urls)
                        telegram_message.save()
                        telegram_message.refresh_from_db()
                    else:
                        logger.warning(f"Не нашлось сообщение от дискорда, {request_text}")
            if all_messages or len(data) == 100:
                account.last_message_id = data[0].get("id")
                account.save()
        else:
            logger.warning(
                f"Не удалось получить сообщения от аккаунта {account.login}, {account.last_message_id}"
            )
    send_messages_to_telegram()


@shared_task
def send_messages_to_telegram():
    """
    Отправка всех ранее не отправленных сообщений в телеграм
    :return:
    """
    not_answered_messages = Message.objects.filter(images__isnull=False).filter(
        Q(seed_send=False, seed__isnull=False) | Q(answer_sent=False)
    )
    for message in not_answered_messages:
        for url in message.images.split(", "):
            if url:
                photo = requests.get(url)
                try:
                    bot.send_photo(chat_id=message.telegram_id, photo=photo.content)
                except Exception:
                    bot.send_message(
                        message.telegram_id,
                        text=f"<a href='{url}'>Скачайте увеличенное фото тут</a>",
                        parse_mode="HTML"
                    )
                    continue
        buttons_markup = types.InlineKeyboardMarkup()
        buttons_markup.row_width = 4
        buttons = []
        for button_key, button_values in message.buttons.items():
            if button_key:
                if message.answer_type == DiscordTypes.START_GEN and button_key.startswith("U"):
                    button_prefix = "button_u"
                    callback_data = f"{button_prefix}&&{button_key}&&{message.id}"
                    item = types.InlineKeyboardButton(
                        button_key,
                        callback_data=callback_data
                    )
                    buttons.append(item)
                elif button_key.startswith("Zoom Out"):
                    button_prefix = "button_zoom"
                    callback_data = f"{button_prefix}&&{button_key}&&{message.id}"
                    item = types.InlineKeyboardButton(
                        button_key,
                        callback_data=callback_data
                    )
                    buttons.append(item)
                # elif button_key.startswith("Upscale (2x)"):
                #     button_prefix = "button_upscale"
                #     callback_data = f"{button_prefix}&&{button_key}&&{message.id}"
                #     item = types.InlineKeyboardButton(
                #         button_key,
                #         callback_data=callback_data
                #     )
                #     buttons.append(item)
        if message.answer_type == DiscordTypes.START_GEN:
            buttons = add_four_pics_buttons(buttons, message.id)
        elif message.answer_type == DiscordTypes.UPSCALED:
            buttons_markup.row_width = 1
            buttons = add_upscaled_pic_buttons(message.id, buttons)
        elif message.answer_type == DiscordTypes.GOT_SEED:
            buttons_markup.row_width = 1
            buttons = add_seed_pic_buttons(buttons, message.id)
        buttons_markup.add(*buttons)

        bot.send_message(message.telegram_id, text=message.text, reply_markup=buttons_markup)
        message.answer_sent = True
        if message.seed:
            message.seed_send = True
        message.save()


@shared_task
def send_message_no_answer():
    messages = Message.objects.filter(
        discord_message_id__isnull=True,
        created_at__lte=now() - timedelta(minutes=30),
        answer_sent=False
    ).select_related("user")
    for message in messages:
        time.sleep(0.5)
        bot.send_message(
            chat_id=message.telegram_id,
            text=f"""
            <pre>❌ Упс! Похоже что-то пошло не так, волшебство не удалось.\n\nМы добавили вам одну генерацию\n\nНапишите новый запрос</pre>
            """,
            parse_mode="HTML"
        )
        message.answer_sent = True
        message.save()
        user = message.user
        user.remain_messages += 1
        user.save()
        user.refresh_from_db()


@shared_task
def delete_old_messages():
    Message.objects.filter(created_at__lt=now() - timedelta(hours=24)).delete()
