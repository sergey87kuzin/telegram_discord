import json
import logging
from http import HTTPStatus

import requests
from discord_messages.models import DiscordAccount, DiscordConnection, Message


logger = logging.getLogger(__name__)


class DiscordHelper:
    def get_discord_auth_data(self, user):
        """
        В зависимости от пользователя проверять, к какому акку дискорда подключен,
        возвращать его настройки
        """
        account = user.account
        return account

    def get_new_connection(self, account):
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
        logger.warning(f"Не могу подключиться: {account.login}, {response.status_code}")
        return


def send_message_to_discord(text, account: DiscordAccount, connection: DiscordConnection) -> int:
    """
    Отправить текст в команду /imagine для получения первых картинок по запросу
    :param text: Текст сообщения в /imagine
    :param account: аккаунт, к которому подключен пользователь
    :param connection: соединение аккаунта с сервером дискорда
    :return:
    """
    discord_url = f"https://discord.com/api/v9/interactions"
    data = {
        "type": 2,
        "application_id": "936929561302675456",
        "channel_id": account.channel_id,
        "session_id": account.session_id,
        "data": {
            "version": "1166847114203123795",
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
                "version": "1166847114203123795",
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


def send_u_line_button_command_to_discord(
        account: DiscordAccount,
        message: Message,
        button_key: str,
        connection: DiscordConnection
):
    """
    Имитация нажатия кнопок верхнего ряда полсле первой генерации (коды кнопок U1-U4)
    :param account:
    :param message:
    :param button_key:
    :param connection:
    :return: status_code
    """
    button = message.buttons.get(button_key)
    discord_url = f"https://discord.com/api/v9/interactions"
    data = {
        "application_id": "936929561302675456",
        "channel_id": account.channel_id,
        "guild_id": None,
        "message_flags": 0,
        "type": 3,
        "session_id": account.session_id,
        "message_id": message.discord_message_id,
        "data": {
            "component_type": button.get("type"),
            "custom_id": button.get("custom_id")
        }
    }
    headers = {
        "Authorization": connection.token,
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.post(discord_url, json=data, headers=headers)
    if response.status_code != HTTPStatus.NO_CONTENT:
        logger.warning(
            f"Неправильно отправлено сообщение в discord,"
            f" {response.status_code}, {response.text}, {account.login}, {message.id}"
        )
    return response.status_code


def send_vary_strong_message(
        account: DiscordAccount,
        message: Message,
        connection: DiscordConnection,
):
    """
    Запрос на сильное изменение картинки
    :param account:
    :param message:
    :param button_key:
    :param connection:
    :return: status_code
    """
    picture = message.images.split(",")[0]
    text = f"{picture} {message.text}"
    Message.objects.create(
        text=message.text,
        eng_text=message.text,
        user_id=message.user_id,
        user_telegram=message.user_telegram,
        telegram_id=message.telegram_id,
    )
    return send_message_to_discord(text=text, account=account, connection=connection)


def send_vary_soft_message(
        account: DiscordAccount,
        message: Message,
        connection: DiscordConnection,
):
    """
    Запрос на слабое изменение картинки
    :param account:
    :param message:
    :param button_key:
    :param connection:
    :return: status_code
    """
    picture = message.images.split(",")[0]
    text = f"{picture} {message.text} --seed {message.seed}"
    Message.objects.create(
        text=message.text,
        eng_text=message.text,
        user_id=message.user_id,
        user_telegram=message.user_telegram,
        telegram_id=message.telegram_id,
    )
    return send_message_to_discord(text=text, account=account, connection=connection)


def get_message_seed(account, connection, message):
    seed_url = f"https://discord.com/api/v9/channels/{account.channel_id}/messages/"\
               f"{message.discord_message_id}/reactions/%E2%9C%89%EF%B8%8F/%40me?location=Message&type=0"
    headers = {
        "Authorization": connection.token,
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.put(seed_url, headers=headers)
    if response.status_code != HTTPStatus.OK:
        logger.warning(f"Не удалось получить сид картинки, {account.login}, {message.id}")
    return response.status_code

