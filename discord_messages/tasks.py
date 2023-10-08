import urllib

import requests
from celery import shared_task

from discord_messages.models import DiscordAccount, Message
from discord_messages.telegram_helper import bot


@shared_task
def get_discord_messages():
    for account in DiscordAccount.objects.all().prefetch_related("connections"):
        get_messages_url = f"https://discord.com/api/v9/channels/{account.channel_id}/messages"
        if account.last_message_id:
            get_messages_url += f"?after={account.last_message_id}&limit=100"
        headers = {"Authorization": account.connections.first().token}
        response = requests.get(get_messages_url, headers=headers)
        if response.ok and response.json():
            data = response.json()
            account.last_message_id = data[0].get("id")
            account.save()
            for discord_message in data:
                attachments_urls = []
                if "**" in discord_message.get("content"):
                    request_text = discord_message.get("content").split("**")[1]
                    if telegram_message := Message.objects.filter(text=request_text).first():
                        telegram_message.discord_message_id = discord_message.get("id")
                        telegram_message.buttons = discord_message.get("components")[0]\
                            .get("components")[0].get("custom_id").split("::")[-1]
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
        message.answer_sent = True
        message.save()
