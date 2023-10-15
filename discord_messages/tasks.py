import urllib

import requests
from celery import shared_task
from telebot import types

from discord_messages.discord_helper import DiscordHelper
from discord_messages.models import DiscordAccount, Message, DiscordConnection
from discord_messages.telegram_helper import bot


@shared_task
def get_discord_messages():
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
            account.last_message_id = data[0].get("id")
            account.save()
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
                        telegram_message.discord_message_id = discord_message.get("id")
                        for line in discord_message.get("components"):
                            for component in line.get("components"):
                                telegram_message.buttons[component.get("label")] = {
                                    "custom_id": component.get("custom_id"),
                                    "type": component.get("type"),
                                    "label": component.get("label"),
                                    "emoji": component.get("emoji")
                                }
                        for attachment in discord_message.get("attachments"):
                            attachments_urls.append(attachment.get("proxy_url").split("?")[0])
                        telegram_message.images = ", ".join(attachments_urls)
                        telegram_message.save()


@shared_task
def send_messages_to_telegram():
    not_answered_messages = Message.objects.filter(answer_sent=False)
    for message in not_answered_messages:
        for url in message.images.split(", "):
            photo = requests.get(url)
            bot.send_photo(chat_id=message.telegram_id, photo=photo.content)
        buttons_markup = types.InlineKeyboardMarkup()
        for button_key, button_values in message.buttons.items():
            if button_key:
                if button_key.startswith("U"):
                    button_prefix = "button_u"
                elif button_key.startswith("V"):
                    button_prefix = "button_v"
                else:
                    button_prefix = "some_button"
                item = types.InlineKeyboardButton(
                    button_key,
                    callback_data=f"{button_prefix}&&{button_key}&&{message.id}"
                )
                buttons_markup.add(item)

        bot.send_message(message.telegram_id, text="Давай сделаем что-то с этим", reply_markup=buttons_markup)
        message.answer_sent = True
        message.save()
