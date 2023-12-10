import random
import logging
import re

import telebot
from deep_translator import GoogleTranslator
from django.conf import settings
from django.db.models import Count
from django.utils.timezone import now
from telebot import types

from bot_config.models import SiteSettings
from discord_messages.choices import DiscordTypes
from discord_messages.constants import INFO_TEXT, PRESET_INFO_TEXT
from discord_messages.denied_words import check_words
from discord_messages.discord_helper import send_u_line_button_command_to_discord, get_message_seed, \
    send_vary_strong_message, send_vary_soft_message, send_message_to_discord, DiscordHelper
from discord_messages.models import ConfirmMessage, Message, DiscordAccount  # , DiscordAccount, DiscordConnection
# from discord_messages.tasks import send_message_to_discord_task
from users.models import User

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)


def send_confirm_code(user: User):
    """
    Отправить код подтверждения для регистрации
    :param user:
    :return:
    """
    random_code = str(random.randint(0, 9999)).zfill(4)
    telegram_id = user.chat_id
    ConfirmMessage.objects.filter(telegram_nick=user.username).update(new_message_sent=True)
    ConfirmMessage.objects.create(
        telegram_nick=user.username,
        code=random_code
    )
    bot.send_message(chat_id=telegram_id, text=random_code)


def handle_start_message(message):
    """
    Обработка сообщения при старте бота
    :param message:
    :return:
    """
    username = message.get("from", {}).get("username")
    chat_id = message.get("chat").get("id")
    if username:
        try:
            user, created = User.objects.get_or_create(
                username__iexact=username,
                chat_id=chat_id,
                defaults={
                    "username": username,
                    "chat_id": chat_id,
                }
            )
            if created:
                user.set_password(str(random.randint(0, 99999999)).zfill(8))
                account = DiscordAccount.objects.aggregate(users_count=Count("users")).order_by("users_count").first()
                user.account = account
                user.save()
        except Exception as e:
            logger.warning(f"Ошибка регистрации пользователя, {username}, {str(e)}")
            bot.send_message(
                chat_id,
                "<pre>Пожалуйста, попробуйте еще раз или напишите админу</pre>",
                parse_mode="HTML"
            )
            return
        site_settings = SiteSettings.get_solo()
        if site_settings.say_hi_video:
            bot.send_video_note(chat_id, site_settings.say_hi_video.file.file)
        bot.send_message(
            chat_id,
            text="https://www.youtube.com/watch?v=PupAadTlhNQ"
        )
        register_reply_markup = types.InlineKeyboardMarkup()
        register_button = types.InlineKeyboardButton(
            "Зарегистрироваться",
            url=f"{settings.SITE_DOMAIN}/auth/registration/{user.id}/"
        )
        register_reply_markup.add(register_button)
        bot.send_message(
            chat_id,
            text="<pre>Привет ✌️ Для продолжения регистрации нажмите на кнопку:</pre>",
            reply_markup=register_reply_markup,
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            chat_id,
            text="""<pre>Упс! У вас в Telegram нет ника.\n▪️Перейдите в свой профиль\n▪️Нажмите «Выбрать имя пользователя»\n▪️Придумайте ник\n▪️После нажмите на кнопку Старт в меню): </pre>""",
            parse_mode="HTML"
        )


def handle_command(message):
    """
    Обработка команд бота
    :param message:
    :return:
    """
    message_text = message.get("text")
    chat_id = message.get("chat").get("id")
    username = message.get("from", {}).get("username")
    if message_text == "/help":
        bot.send_message(
            chat_id,
            f"""<pre>Для того, чтобы начать генерацию, просто вводите текст промпта\nДля того, чтобы поменять пароль, введите /password новый пароль\nПереход на сайт: {settings.SITE_DOMAIN}</pre>""",
            parse_mode="HTML"
        )
        return
    if message_text.startswith("/password"):
        password = message_text.replace("/password ", "")
        if password and password != " ":
            user = User.objects.filter(username=username, is_active=True).first()
            if not user:
                bot.send_message(
                    chat_id,
                    f"<pre>Перейдите на сайт и зарегистрируйтесь</pre>",
                    parse_mode="HTML"
                )
                return
            user.set_password(password)
            user.save()
            bot.send_message(
                chat_id,
                f"<pre>Ваш новый пароль {password}</pre>",
                parse_mode="HTML"
            )
            return
    if message_text.startswith("/preset"):
        preset = message_text.replace("/preset", "")
        if preset and preset != " ":
            user = User.objects.filter(username=username).first()
            if preset.endswith("delete"):
                user.preset = ""
                user.save()
                bot.send_message(
                    chat_id,
                    "<pre>Суффикс удален</pre>",
                    parse_mode="HTML"
                )
                return
            preset = preset.replace("  ", " ").replace("—", "--").replace(" ::", "::").replace("-- ", "--")
            if re.findall("::\S+", preset):
                preset = preset.replace("::", ":: ")
            if not preset.startswith(" "):
                preset = f" {preset}"
            try:
                user.preset = preset
                user.save()
            except Exception:
                bot.send_message(
                    chat_id,
                    "<pre>Некорректное значение</pre>",
                    parse_mode="HTML"
                )
                return
            bot.send_message(
                chat_id,
                f"<pre>Установлен новый суффикс: '{preset }'</pre>",
                parse_mode="HTML"
            )
            return
        bot.send_message(
            chat_id,
            "<pre>Некорректное значение</pre>",
            parse_mode="HTML"
        )
    if message_text == "/format":
        presets = (
            ("3:2",  " --ar 3:2"),
            ("2:3", " --ar 2:3"),
            ("16:9", " --ar 16:9"),
            ("9:16", " --ar 9:16"),
            ("3:1", " --ar 3:1"),
            ("Удалить", "preset&&del"),
            ("Инфо", "preset&&info")
        )
        buttons_menu_markup = types.InlineKeyboardMarkup()
        buttons_menu_markup.row_width = 4
        buttons = []
        for preset in presets:
            format_button = types.InlineKeyboardButton(
                preset[0],
                callback_data=f"preset&&{preset[1]}"
            )
            buttons.append(format_button)
        buttons_menu_markup.add(*buttons)
        bot.send_message(
            chat_id,
            "<pre>Какой формат изображения будет?</pre>",
            reply_markup=buttons_menu_markup,
            parse_mode="HTML"
        )
        return
    if message_text == "/mybot":
        user = User.objects.filter(username__iexact=username, is_active=True).first()
        if not user:
            bot.send_message(
                chat_id,
                text="<pre>Ваш аккаунт не найден. Обратитесь в поддержку</pre>",
                parse_mode="HTML"
            )
        info_text = f"""<pre>Доступ до: {user.get_bot_end}\nДоступные генерации: {user.all_messages}\n</pre>"""
        my_bot_reply_markup = types.InlineKeyboardMarkup()
        buttons = []
        del_format_button = types.InlineKeyboardButton(
            "Продлить",
            url=settings.SITE_DOMAIN
        )
        buttons.append(del_format_button)
        my_bot_reply_markup.add(*buttons)
        bot.send_message(
            chat_id,
            text=info_text,
            reply_markup=my_bot_reply_markup,
            parse_mode="HTML"
        )
        return
    if message_text == "/instruction":
        info_reply_markup = types.InlineKeyboardMarkup()
        buttons = []
        info_button = types.InlineKeyboardButton(
            "Перейти на сайт",
            url=settings.SITE_DOMAIN
        )
        buttons.append(info_button)
        info_reply_markup.add(*buttons)
        bot.send_message(chat_id, text=INFO_TEXT, reply_markup=info_reply_markup, parse_mode="HTML")
        return
    if message_text == "/support":
        bot.send_message(chat_id, text="Мы работаем над этим")
        return
    if message_text == "/payment":
        bot.send_message(chat_id, text="Чуть позже")
        return
    if message_text == "/lessons":
        bot.send_message(
            chat_id,
            text=f"{settings.SITE_DOMAIN}/courses/course/2/",
        )
        return
    bot.send_message(chat_id, "Некорректное значение")


def preset_handler(chat_id, chat_username, message_text):
    preset = message_text.split("&&")[-1]
    user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
    if not user:
        bot.send_message(chat_id, text="Ваш аккаунт не найден. Обратитесь в поддержку")
        return
    if preset == "info":
        info_text = PRESET_INFO_TEXT
        bot.send_message(chat_id, text=info_text, parse_mode="HTML")
    elif preset == "del":
        user.preset = ""
        user.save()
        bot.send_message(chat_id, text="Формат удален")
    else:
        user.preset = preset
        user.save()
        bot.send_message(chat_id, text=f"Установлен формат {preset}")


def add_four_pics_buttons(buttons: list, message_id: int):
    """
    Добавляем кнопки сообщению с 4 картинками
    :param buttons:
    :param message_id:
    :return:
    """
    refresh_item = types.InlineKeyboardButton(
        "Сгенерировать снова",
        callback_data=f"button_send_again&&{message_id}"
    )
    buttons.append(refresh_item)
    return buttons


def add_upscaled_pic_buttons(message_id: int, buttons: list):
    """
    Добавляем кнопки увеличенной одной картинке
    :param message_id:
    :param buttons:
    :return:
    """
    # Вместо кнопки вариаций добавляем сразу кнопку изменений(ту, что без сида)
    # change_item = types.InlineKeyboardButton(
    #     "Вариации",
    #     callback_data=f"button_change&&{message_id}"
    # )
    strong_vary_item = types.InlineKeyboardButton(
        "Изменение",
        callback_data=f"button_vary_strong&&{message_id}"
    )
    buttons.append(strong_vary_item)
    return buttons


def add_seed_pic_buttons(buttons: list, message_id: int):
    """
    добавляем кнопки картинке с полученным сидом
    :return:
    """
    buttons = []
    strong_vary_item = types.InlineKeyboardButton(
        "Сильное изменение",
        callback_data=f"button_vary_strong&&{message_id}"
    )
    soft_vary_item = types.InlineKeyboardButton(
        "Слабое изменение",
        callback_data=f"button_vary_soft&&{message_id}"
    )
    buttons.append(strong_vary_item)
    buttons.append(soft_vary_item)
    return buttons


def choose_action(account, connection, message_text):
    if message_text.startswith("button_u&&") or message_text.startswith("button_zoom&&"):
        logger.warning(f"button zoom info: {message_text}")
        button_data = list(message_text.split("&&"))
        message = Message.objects.filter(id=button_data[2]).first()
        if not message:
            logger.warning(f"Не нашлось сообщение, {message_text}")
        status = send_u_line_button_command_to_discord(
            account=account,
            connection=connection,
            button_key=button_data[1],
            message=message
        )
    elif message_text.startswith("button_change&&"):
        logger.warning(f"button change info: {message_text}")
        button_data = list(message_text.split("&&"))
        message = Message.objects.filter(id=button_data[-1]).first()
        if not message:
            logger.warning(f"Не нашлось сообщение, {message_text}")
        status = get_message_seed(account, connection, message)
    elif message_text.startswith("button_vary_strong&&"):
        logger.warning(f"button vary info: {message_text}")
        button_data = list(message_text.split("&&"))
        message = Message.objects.filter(id=button_data[-1]).first()
        if not message:
            logger.warning(f"Не нашлось сообщение, {message_text}")
        status = send_vary_strong_message(
            message=message, account=account, connection=connection
        )
    elif message_text.startswith("button_vary_soft&&"):
        logger.warning(f"button vary soft info: {message_text}")
        button_data = list(message_text.split("&&"))
        message = Message.objects.filter(id=button_data[-1]).first()
        if not message:
            logger.warning(f"Не нашлось сообщение, {message_text}")
        status = send_vary_soft_message(
            message=message, account=account, connection=connection
        )
    else:
        logger.warning(f"message info: {message_text}")
        status = send_message_to_discord(message_text, account, connection)
    return status


def handle_message(request_data):
    translator = GoogleTranslator(source='auto', target='en')
    answer_text = "Творим волшебство"
    message = request_data.get("message")
    if message:
        chat_id = message.get("chat", {}).get("id")
        message_text = message.get("text")
        if not message_text:
            bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы отправили пустое сообщение</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        if message_text == "/start":
            handle_start_message(message)
            return "", "", ""
        if message_text.startswith("/"):
            handle_command(message)
            return "", "", ""
        message_text = message.get("text")\
            .replace("—", "--").replace(" ::", "::").replace("  ", " ").replace("-- ", "--")
        if re.findall("::\S+", message_text):
            message_text = message_text.replace("::", ":: ")
        after_create_message_text = message_text
        chat_username = message.get("chat", {}).get("username")
        if not message_text or not chat_username or not chat_id:
            logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
            bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы отправили пустое сообщение</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        eng_text = translator.translate(message_text)
        if not eng_text:
            logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
            bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы отправили пустое сообщение</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        wrong_words = check_words(eng_text)
        if wrong_words:
            bot.send_message(
                chat_id=chat_id,
                text=f"<pre>❌Вы отправили запрещенные слова: {wrong_words}</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        eng_text = eng_text.replace("-- ", "--")
        no_ar_text = eng_text.split(" --")[0]
        message_type = DiscordTypes.START_GEN
        user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
        if not user:
            logger.warning(f"Не найден пользователь(, user = {chat_username}")
            bot.send_message(
                chat_id=chat_id,
                text="<pre>Вы не зарегистрированы в приложении</pre>",
                parse_mode="HTML"
            )
            return "", "", ""
        if user.preset and user.preset not in message_text and user.preset not in eng_text:
            message_text = message_text + user.preset
            eng_text = eng_text + user.preset
    else:
        button_data = request_data.get("callback_query")
        if button_data:
            chat_id = button_data.get("from", {}).get("id")
            message_text = button_data.get("data")
            if Message.objects.filter(eng_text=message_text).exists():
                bot.send_message(chat_id=chat_id, text="Вы уже нажимали на эту кнопку)")
                return "", "", ""
            chat_username = button_data.get("from", {}).get("username")
            if message_text.startswith("preset&&"):
                preset_handler(chat_id, chat_username, message_text)
                return "", "", ""
            reply_markup = button_data.get("message").get("reply_markup")
            buttons_markup = types.InlineKeyboardMarkup()
            buttons_markup.row_width = len(reply_markup.get("inline_keyboard")[0])
            buttons = []
            for line in reply_markup.get("inline_keyboard"):
                for button in line:
                    if button.get("callback_data") == button_data.get("data"):
                        item = types.InlineKeyboardButton(
                            "✅",
                            callback_data=button.get("callback_data")
                        )
                    else:
                        item = types.InlineKeyboardButton(
                            button.get("text"),
                            callback_data=button.get("callback_data")
                        )
                    buttons.append(item)
            buttons_markup.add(*buttons)
            try:
                bot.edit_message_reply_markup(
                    message_id=button_data.get("message").get("message_id"),
                    reply_markup=buttons_markup,
                    chat_id=chat_id
                )
            except Exception:
                pass
            if not message_text or not chat_username or not chat_id:
                logger.warning(f"Ошибка кнопки чата. {chat_id}, {chat_username}, {message_text}")
                bot.send_message(chat_id=chat_id, text="С этой кнопкой что-то не так")
                return "", "", ""
            eng_text = message_text
            user = User.objects.filter(username__iexact=chat_username).first()
            if not user:
                logger.warning(f"Не найден пользователь(, user = {chat_username}")
                bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
                return "", "", ""
            first_message = Message.objects.filter(id=message_text.split("&&")[-1]).first()
            message_type = DiscordTypes.UPSCALED
            # переменная для определения типа сообщения после создания
            after_create_message_text = message_text
            # if message_text.startswith("button_upscale"):
            #     url = "https://ya.ru/search/?text=topaz+gigapixel+ai&lr=2&" \
            #           "search_source=yaru_desktop_common&search_domain=yaru&src=suggest_B"
            #     bot.send_message(
            #         chat_id=chat_id,
            #         text=f"<a href='{url}'>Upscale временно недоступен, используйте топаз</a>",
            #         parse_mode="HTML"
            #     )
            #     return "", "", ""
            if message_text.startswith("button_u&&"):
                answer_text = "Увеличиваем"
            if message_text.startswith(("button_zoom&&", "button_vary", "button_upscale")):
                message_text = first_message.text
                answer_text = "Делаем вариации" if message_text.startswith("button_vary") else "Отдаляем"
                message_type = DiscordTypes.START_GEN
            elif message_text.startswith("button_change&&"):
                message_text = first_message.text
                message_type = DiscordTypes.START_GEN
            elif message_text.startswith("button_send_again&&"):
                message_text = first_message.eng_text
                eng_text = first_message.eng_text
                message_type = DiscordTypes.START_GEN
            else:
                message_text = first_message.eng_text
            no_ar_text = first_message.no_ar_text
        else:
            user = User.objects.first()
            bot.send_message(
                chat_id=user.chat_id,
                text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
            )
            return "", "", ""
    if not message_text.startswith("button_u&&"):
        if user.remain_messages == 0:
            if not user.date_of_payment or user.date_payment_expired < now():
                bot.send_message(
                    chat_id=chat_id,
                    text="Пожалуйста, оплатите доступ к боту",
                )
                return "", "", ""
        if user.remain_paid_messages > 0:
            user.remain_paid_messages -= 1
            user.save()
        elif user.remain_messages > 0:
            user.remain_messages -= 1
            user.save()
        else:
            bot.send_message(
                chat_id=chat_id,
                text="У вас не осталось генераций",
            )
            return "", "", ""
    created_message = Message.objects.create(
        text=message_text,
        eng_text=eng_text,
        no_ar_text=no_ar_text,
        user_telegram=chat_username,
        telegram_id=chat_id,
        user=user,
        answer_type=message_type
    )
    if after_create_message_text.startswith(("button_zoom&&", "button_vary", "button_upscale")):
        created_message.eng_text = created_message.text
        created_message.no_ar_text = created_message.text.split(" --")[0]
        created_message.save()
    bot.send_message(chat_id=chat_id, text=answer_text)
    return user, eng_text, chat_id
