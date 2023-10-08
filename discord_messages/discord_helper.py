import json
from http import HTTPStatus

import requests
from django.conf import settings

from discord_messages.models import DiscordAccount, DiscordConnection


class DiscordHelper:
    def get_discord_auth_data(self, user):
        """
        В зависимости от пользователя проверять, к какому акку дискорда подключен,
        возвращать его настройки
        """
        account = DiscordAccount.objects.first()
        return account

    def get_new_connection(self, user):
        account = self.get_discord_auth_data(user)
        login_url = "https://discord.com/api/v9/auth/login"
        data = {
            "gift_code_sku_id": None,
            "login": account.login,
            "login_source": None,
            "password": account.password,
            "undelete": False
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(login_url, data=json.dumps(data), headers=headers)
        if response.status_code == HTTPStatus.OK:
            response_data = response.json()
            user_id = response_data.get("user_id")
            token = response_data.get("token")
            connection, created = DiscordConnection.objects.update_or_create(
                account=account,
                defaults={
                    "account": account,
                    "token": token,
                    "channel_id": user_id
                }
            )
            return connection
        return


def send_message_to_discord(text, account: DiscordAccount, connection: DiscordConnection):
    discord_url = f"https://discord.com/api/v9/interactions"
    data = {
        "type": 2,
        "application_id": "936929561302675456",
        "channel_id": account.channel_id,
        "session_id": account.session_id,
        "data": {
            "version": "1118961510123847772",
            "id": "938956540159881230",
            "name": "imagine",
            "type": 1,
            "options": [{
                "type": 3,
                "name": "prompt",
                "value": text
            }],
            "application_command": {
                "id": "938956540159881230",
                "application_id": "936929561302675456",
                "version": "1118961510123847772",
                "default_member_permissions": None,
                "type": 1,
                "nsfw": False,
                "name": "imagine",
                "description": "Create images with Midjourney",
                "dm_permission": True,
                "contexts": [0, 1, 2],
                "integration_types": [0],
                "options": [{
                    "type": 3,
                    "name": "prompt",
                    "description": "The prompt to imagine",
                    "required": True
                }]
            },
            "attachments": []
        },
    }
    headers = {
        "Authorization": connection.token,
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.post(discord_url, json=data, headers=headers)
    return response.status_code
