import random
import logging
import re
import time
from http import HTTPStatus

import telebot
from deep_translator import GoogleTranslator
from django.conf import settings
from django.utils.timezone import now
from rest_framework.response import Response
from telebot import types

from discord_messages.choices import DiscordTypes
from discord_messages.discord_helper import send_u_line_button_command_to_discord, get_message_seed, \
    send_vary_strong_message, send_vary_soft_message, send_message_to_discord, DiscordHelper
from discord_messages.models import ConfirmMessage, Message, DiscordAccount, DiscordConnection
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
                user.save()
        except Exception as e:
            logger.warning(f"Ошибка регистрации пользователя, {username}, {str(e)}")
            bot.send_message(chat_id, "Пожалуйста, попробуйте еще раз или напишите админу")
            return
        bot.send_message(
            chat_id,
            "Привет) Наташа напишет, когда можно будет начинать веселье)"
            # (f"Привет ✌️ Для продолжения регистрации перейдите по ссылке: {settings.SITE_DOMAIN}"
            #  f"/auth/registration/{user.id}/")
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
            f"""Для того, чтобы начать генерацию, просто вводите текст промпта\n
                Для того, чтобы поменять пароль, введите /newpassword новый пароль\n
                Личный кабинет: {settings.SITE_DOMAIN},\n
                Техподдержка: {settings.TECH_BOT_URL}
            """
        )
        return
    if message_text.startswith("/preset"):
        preset = message_text.replace("/preset", "")
        if preset and preset != " ":
            user = User.objects.filter(username=username).first()
            if preset.endswith("delete"):
                user.preset = ""
                user.save()
                bot.send_message(chat_id, "Суффикс удален")
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
                bot.send_message(chat_id, "Некорректное значение")
                return
            bot.send_message(chat_id, f"Установлен новый суффикс: '{preset }'")
            return
        bot.send_message(chat_id, "Некорректное значение")
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
        bot.send_message(chat_id, "Какой формат изображения будет?", reply_markup=buttons_menu_markup)
        return
    if message_text == "/mybot":
        user = User.objects.filter(username__iexact=username, is_active=True).first()
        if not user:
            bot.send_message(chat_id, text="Ваш аккаунт не найден. Обратитесь в поддержку")
        info_text = f"""
        Доступ до: {user.get_bot_end}\n
        Доступные генерации: {user.remain_messages}\n
        """
        my_bot_reply_markup = types.InlineKeyboardMarkup()
        buttons = []
        del_format_button = types.InlineKeyboardButton(
            "Продлить",
            # Установить нужную ссылку для продления
            url="https://ya.ru"
        )
        buttons.append(del_format_button)
        my_bot_reply_markup.add(*buttons)
        bot.send_message(chat_id, text=info_text, reply_markup=my_bot_reply_markup)
        return
    if message_text == "/instruction":
        instruction_text = """
        ▪️Бот рисует в нейросети Midjourney v.5.2

        ✅ 10 подарочных генераций каждый месяц 1 числа. Подарки не суммируются и сгорают в конце месяца.

        ▪️Полученные изображения можно загружать на фотобанки для продажи. AdobeStock, FreePik, 123rf, Dreamstime

        Как генерировать изображения?

        ▪️1. Боту можно писать на русском и английском языке

        ▪️2. Напишите, что вы хотите увидеть на изображении

        ▪️ 3. Самое главное по смыслу слово всегда ставьте ближе к началу запроса

        ▪️ 4. Чем более полным будет описание, тем легче нейросети рисовать

        ▪️ 5. Можно добавлять стили изображений и параметры съемки в запрос

        ▪️ 6. Выберите в меню формат изображения

        ▪️ 7. Увеличить понравившийся кадр можно кнопками U1,U2,U3,U4

        ▪️ 8. После увеличения U1,U2,U3,U4 изображения имеют размер:
            1:1      1024 х 1024 px
            3:2      1344 х 896 px
            16:9     1456 x 816 px
            3:1      1904 x 640 px

        ▪️ 9. После увеличения изображение можно отдалить(ZoomOut), увеличить в 2 раза(Upscale2x) и изменить его, сделав вариации.

        ✅ 10. Увеличивайте то, что вам нравится, СРАЗУ, чтобы не потерять.

        ❌ 11. Кнопки под изображениями активны в течение суток от создания изображения.

        ▪️ 12. Созданные и увеличенные изображения из бота не пропадают, сохранить на устройство вы сможете через любое время.

        ▪️ 13. Каждая операция Upscale(2x) занимает 4 минуты и дольше, если вы генерите много изображений, лучше сохранять их на устройство после U1,U2,U3,U4, а увеличивать пакетно в программе Topaz Gigapixel 

        ‼️ Когда готово будет‼️▪️ 14. Вы можете добавить свое изображение и написать запрос для нейросети, бот нарисует новое изображение на основе вашего.

        ⏰ Терпение! Время генерации от 1 до 15 минут.

        На сайте: 
        ✅подробные видеоинструкции про работу с ботом, шпаргалки описаний, стилей, запрещенных слов 

        ✅как продавать картинки через интернет на фотобанках
        """
        info_reply_markup = types.InlineKeyboardMarkup()
        buttons = []
        info_button = types.InlineKeyboardButton(
            "Перейти на сайт",
            # Установить нужную ссылку для продления
            url="https://ya.ru"
        )
        buttons.append(info_button)
        info_reply_markup.add(*buttons)
        bot.send_message(chat_id, text=instruction_text, reply_markup=info_reply_markup)
        return
    if message_text == "/support":
        bot.send_message(chat_id, text="Мы работаем над этим")
        return
    if message_text == "/payment":
        bot.send_message(chat_id, text="Чуть позже")
        return
    if message_text == "/lessons":
        bot.send_message(chat_id, text="Чуть позже")
        return
    bot.send_message(chat_id, "Некорректное значение")


def preset_handler(chat_id, chat_username, message_text):
    preset = message_text.split("&&")[-1]
    user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
    if not user:
        bot.send_message(chat_id, text="Ваш аккаунт не найден. Обратитесь в поддержку")
        return
    if preset == "info":
        info_text = """
        ▪️По умолчанию изображения создаются квадратными 1:1

        ▪️Ваши изображения будут создаваться в выбранном формате до тех пор, пока вы не выберете другой, либо не удалите выбранный.

        ▪️Чтобы создавать изображения в любом другом формате, нужно удалить предыдущий и дописать в конце запроса « --ar 4:5» (или по-русски « --ар 4:5») , где  4:5 - соотношение сторон. Собственный формат не сохраняется, добавлять к запросу каждый раз."""
        bot.send_message(chat_id, text=info_text)
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
    change_item = types.InlineKeyboardButton(
        "Вариации",
        callback_data=f"button_change&&{message_id}"
    )
    buttons.append(change_item)
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
            bot.send_message(chat_id=chat_id, text="Вы отправили пустое сообщение")
            return Response(HTTPStatus.BAD_REQUEST)
        if message_text == "/start":
            handle_start_message(message)
            return Response(HTTPStatus.OK)
        if message_text.startswith("/"):
            handle_command(message)
            return Response(HTTPStatus.OK)
        message_text = message.get("text")\
            .replace("—", "--").replace(" ::", "::").replace("  ", " ").replace("-- ", "--")
        if re.findall("::\S+", message_text):
            message_text = message_text.replace("::", ":: ")
        after_create_message_text = message_text
        chat_username = message.get("chat", {}).get("username")
        if not message_text or not chat_username or not chat_id:
            logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
            bot.send_message(chat_id=chat_id, text="Вы отправили пустое сообщение")
            return Response(HTTPStatus.BAD_REQUEST)
        eng_text = translator.translate(message_text)
        if not eng_text:
            logger.warning(f"Ошибка входящего сообщения. {chat_id}, {chat_username}, {message_text}")
            bot.send_message(chat_id=chat_id, text="Вы отправили пустое сообщение")
            return Response(HTTPStatus.BAD_REQUEST)
        no_ar_text = eng_text.split(" --")[0]
        message_type = DiscordTypes.START_GEN
        user = User.objects.filter(username__iexact=chat_username, is_active=True).first()
        if not user:
            logger.warning(f"Не найден пользователь(, user = {chat_username}")
            bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
            return Response(HTTPStatus.BAD_REQUEST)
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
            chat_username = button_data.get("from", {}).get("username")
            if message_text.startswith("preset&&"):
                preset_handler(chat_id, chat_username, message_text)
                return Response(HTTPStatus.OK)
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
                return Response(HTTPStatus.BAD_REQUEST)
            eng_text = message_text
            user = User.objects.filter(username__iexact=chat_username).first()
            if not user:
                logger.warning(f"Не найден пользователь(, user = {chat_username}")
                bot.send_message(chat_id=chat_id, text="Вы не зарегистрированы в приложении")
                return Response(HTTPStatus.BAD_REQUEST)
            first_message = Message.objects.filter(id=message_text.split("&&")[-1]).first()
            message_type = DiscordTypes.UPSCALED
            # переменная для определения типа сообщения после создания
            after_create_message_text = message_text
            if message_text.startswith("button_upscale"):
                url = "https://ya.ru/search/?text=topaz+gigapixel+ai&lr=2&" \
                      "search_source=yaru_desktop_common&search_domain=yaru&src=suggest_B"
                bot.send_message(
                    chat_id=chat_id,
                    text=f"<a href='{url}'>Upscale временно недоступен, используйте топаз</a>",
                    parse_mode="HTML"
                )
                return Response(HTTPStatus.OK)
            if message_text.startswith("button_u&&"):
                answer_text = "Увеличиваем"
            if message_text.startswith("button_zoom&&") or message_text.startswith("button_vary"):
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
            return Response(HTTPStatus.BAD_REQUEST)
    if not user.date_of_payment or user.date_payment_expired < now():
        bot.send_message(
            chat_id=chat_id,
            text="Пожалуйста, оплатите доступ к боту",
        )
        return Response(HTTPStatus.BAD_REQUEST)
    created_message = Message.objects.create(
        text=message_text,
        eng_text=eng_text,
        no_ar_text=no_ar_text,
        user_telegram=chat_username,
        telegram_id=chat_id,
        user=user,
        answer_type=message_type
    )
    account = DiscordAccount.objects.filter(users=user).first()
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
                text="Неполадки с midjourney(( Попробуйте позже или обратитесь к менеджеру",
            )
            logger.warning(f"Не удалось отправить сообщение, {account.login}, {status}")
            return Response(HTTPStatus.OK)
    if after_create_message_text.startswith(("button_zoom&&", "button_vary")):
        created_message.eng_text = created_message.text
        created_message.no_ar_text = created_message.text.split(" --")[0]
        created_message.save()
    bot.send_message(chat_id=chat_id, text=answer_text)
