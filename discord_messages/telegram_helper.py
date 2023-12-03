import random
import logging
import re

import telebot
from django.conf import settings
from telebot import types

from discord_messages.models import ConfirmMessage
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
        presets = (("3:2",  " --ar 3:2"), ("2:3", " --ar 2:3"), ("16:9", " --ar 16:9"), ("9:16", " --ar 9:16"))
        buttons_menu_markup = types.InlineKeyboardMarkup()
        buttons_menu_markup.row_width = 3
        buttons = []
        for preset in presets:
            format_button = types.InlineKeyboardButton(
                preset[0],
                callback_data=f"preset&&{preset[1]}"
            )
            buttons.append(format_button)
        del_format_button = types.InlineKeyboardButton(
            "Удалить",
            callback_data="preset&&del"
        )
        buttons.append(del_format_button)
        info_format_button = types.InlineKeyboardButton(
            "Инфо",
            callback_data="preset&&info"
        )
        buttons.append(info_format_button)
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
