import urllib

import requests
from celery import shared_task
from telebot import types

from discord_messages.choices import DiscordTypes
from discord_messages.discord_helper import DiscordHelper
from discord_messages.models import DiscordAccount, Message, DiscordConnection
from discord_messages.telegram_helper import bot, add_four_pics_buttons, add_upscaled_pic_buttons, add_seed_pic_buttons


@shared_task
def get_discord_messages():
    """
    Получаем непрочитанные сообщения, определяем их тип(первоначальная генерация 4 картинок
    или увеличение одной(от этого зависят кнопки под картинкой)
    :return:
    """
    for account in DiscordAccount.objects.all().prefetch_related("connections"):
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
            data = response.json()
            for discord_message in data:
                attachments_urls = []
                content = discord_message.get("content")
                if "**" in content:
                    request_text = content.split("**")[1]
                    if telegram_message := Message.objects.filter(text=request_text).first():
                        if "** - Image #" in content:
                            button_number = content.split("** - Image #")[-1][0]
                            request_text = f"button_u&&U{button_number}&&{telegram_message.id}"
                            telegram_message = Message.objects.filter(text=request_text).first()
                            if not telegram_message:
                                continue
                            telegram_message.answer_type = DiscordTypes.UPSCALED
                        elif "**seed**" in content:
                            message_data = content.split("**")
                            message_text = message_data[1]
                            seed = message_data[-1]
                            telegram_message = Message.objects.filter(text=message_text).first()
                            if not telegram_message:
                                continue
                            telegram_message.seed = seed
                            telegram_message.answer_type = DiscordTypes.GOT_SEED
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
                        for attachment in discord_message.get("attachments"):
                            attachments_urls.append(attachment.get("proxy_url").split("?")[0])
                        telegram_message.images = ", ".join(attachments_urls)
                        telegram_message.save()
            account.last_message_id = data[0].get("id")
            account.save()


@shared_task
def send_messages_to_telegram():
    not_answered_messages = Message.objects.filter(answer_sent=False, images__isnull=False)
    for message in not_answered_messages:
        for url in message.images.split(", "):
            photo = requests.get(url)
            bot.send_photo(chat_id=message.telegram_id, photo=photo.content)
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
        if message.answer_type == DiscordTypes.START_GEN:
            buttons = add_four_pics_buttons(buttons, message.eng_text or message.text)
        elif message.answer_type == DiscordTypes.UPSCALED:
            buttons = add_upscaled_pic_buttons(message.id, buttons)
        elif message.answer_type == DiscordTypes.GOT_SEED:
            buttons = add_seed_pic_buttons(buttons, message.id)
        buttons_markup.add(*buttons)

        bot.send_message(message.telegram_id, text="Давай сделаем что-то с этим", reply_markup=buttons_markup)
        message.answer_sent = True
        message.save()
