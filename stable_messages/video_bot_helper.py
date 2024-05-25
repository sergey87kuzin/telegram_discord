import requests
import telebot
from django.db.models import Count

from bot_config.models import SiteSettings
from discord_messages.models import DiscordAccount
from orders.helper import create_prodamus_order_object
from orders.models import Order
from stable_messages.video_bot_menu import VideoBotMenu
from telegram_to_discord import settings
from users.models import User


bot = telebot.TeleBot(settings.FIREWORKS_TELEGRAM_TOKEN)


def create_order_from_video_bot_menu(tariff: str, user: User):
    if tariff == "/testpay":
        bot.send_message(
            user.chat_id,
            text="<pre>Тестовая оплата применяется только один раз</pre>",
            parse_mode="HTML"
        )
    if tariff == "/testpay" and user.used_test_video_payment:
        bot.send_message(
            user.chat_id,
            text="<pre>Вы уже использовали тестовую оплату</pre>",
            parse_mode="HTML"
        )
        return
    TARIFF_COSTS = {
        "/testpay": {
            "cost": 100,
            "message_count": 4
        },
        "/pay25": {
            "cost": 1000,
            "message_count": 25
        },
        "/pay85": {
            "cost": 2975,
            "message_count": 85
        },
        "/pay150": {
            "cost": 4500,
            "message_count": 150
        }
    }
    order_data = TARIFF_COSTS.get(tariff)
    if not order_data:
        return ""
    order = Order.objects.create(
        user=user,
        total_cost=order_data.get("cost"),
        video_message_count=order_data.get("message_count")
    )
    order_string = create_prodamus_order_object(order)
    response = requests.get(
        url=settings.PAYMENT_URL + order_string,
        headers={
            "Content-type": "text/plain;charset=utf-8"
        },
    )
    order.payment_url = response.text
    order.save()
    return response.text


def handle_start_command_video_bot(chat_id: str, chat_username: str):
    site_settings = SiteSettings.get_solo()
    user, created = User.objects.get_or_create(
        username__iexact=chat_username,
        chat_id=chat_id,
        defaults={
            "username": chat_username,
            "chat_id": chat_id,
            "is_active": True
        }
    )
    if created:
        account = DiscordAccount.objects.annotate(users_count=Count("users")).order_by("users_count").first()
        user.account = account
        user.stable_account_id = 1
        user.save()
    bot.send_message(
        chat_id,
        text="Добро пожаловать"
    )
    if site_settings.say_hi_video_video_bot:
        try:
            bot.send_video_note(chat_id, site_settings.say_hi_video_video_bot.file.file)
        except Exception:
            pass
    bot.send_message(
        chat_id,
        text=site_settings.settings_lesson_link
    )


def handle_command_video_bot(user: User, message_text: str):
    if message_text == "/using":
        bot.send_message(
            user.chat_id,
            text=VideoBotMenu.HOW_TO_USE,
            parse_mode="HTML"
        )
    elif message_text == "/settings":
        site_settings = SiteSettings.get_solo()
        bot.send_message(
            user.chat_id,
            text=site_settings.settings_lesson_link or "Пока нет ссылки",
        )
    elif message_text == "/mybot":
        bot.send_message(
            user.chat_id,
            text=f"<pre>Доступные анимации: {user.remain_video_messages} шт.</pre>",
            parse_mode="HTML"
        )
    elif message_text == "/support":
        bot.send_message(
            user.chat_id,
            text=VideoBotMenu.TECH_SUPPORT,
            parse_mode="HTML"
        )
        bot.send_message(
            user.chat_id,
            text="@ai_stocker_help_bot"
        )
    elif message_text == "/images":
        bot.send_message(
            user.chat_id,
            text=VideoBotMenu.IMAGE_BOT,
            parse_mode="HTML"
        )
        bot.send_message(
            user.chat_id,
            text="@tomidjourneybot"
        )
    elif message_text == "/info":
        bot.send_message(
            user.chat_id,
            text=VideoBotMenu.INFO,
            parse_mode="HTML"
        )
    elif message_text in ("/testpay", "/pay25", "/pay85", "/pay150"):
        payment_url = create_order_from_video_bot_menu(message_text, user)
        if not payment_url:
            bot.send_message(user.chat_id, text="Невозможно создать ссылку, обратитесь в техподдержку")
            return
        bot.send_message(
            user.chat_id,
            text=f"<a href='{payment_url}'>Ссылка на оплату</a>",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            user.chat_id,
            text="Интересная, но неизвестная команда :)",
            parse_mode="HTML"
        )
