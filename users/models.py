from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from discord_messages.models import DiscordAccount
from stable_messages.choices import StableModels
from users.managers import CustomUserManager


class Style(models.Model):
    name_for_menu = models.CharField("Название для меню", max_length=128, default="Стиль")
    name = models.CharField("Название", max_length=128)
    positive_prompt = models.CharField("Позитивный промпт", max_length=2048)
    negative_prompt = models.CharField("Негативный промпт", max_length=2048)

    class Meta:
        verbose_name = "Стиль"
        verbose_name_plural = "Стили"

    def __str__(self):
        return self.name


class CustomSettings(models.Model):
    name = models.CharField("Название настроек", max_length=128, default="Какие-то настройки")
    model_id = models.CharField(
        "Номер модели",
        max_length=256,
        blank=True,
        null=True,
        # choices=StableModels.CHOICES,
        default=StableModels.JUGGERNAUT
    )
    seed = models.CharField("Сид", max_length=128, blank=True, null=True, default="-1")
    num_inference_steps = models.CharField("Число шагов", max_length=8, blank=True, null=True, default="20")
    guidance_scale = models.PositiveIntegerField("Шкала", default=7)
    embeddings_model = models.CharField("Связанная модель", max_length=256, blank=True, null=True)
    negative_prompt = models.CharField("Негативный промпт", max_length=2048, blank=True, null=True)
    positive_prompt = models.CharField("Позитивный промпт", max_length=2048, blank=True, null=True)
    lora_model = models.CharField("Модель Лора", max_length=256, blank=True, null=True)
    lora_strength = models.CharField("lora strength", max_length=128, blank=True, null=True)
    sampling_method = models.CharField("Метод семплинга", max_length=256, blank=True, null=True)
    algorithm_type = models.CharField("Тип алгоритма", max_length=256, blank=True, null=True)
    scheduler = models.CharField("scheduler", max_length=256, blank=True, null=True)
    vary_num_inference_steps = models.CharField("Вариации число шагов", max_length=16, blank=True, null=True)
    vary_guidance_scale = models.FloatField("Вариации шкала(7.5)", blank=True, null=True)
    vary_strength = models.FloatField("Вариации сила картинки", blank=True, null=True)
    controlnet_model = models.CharField("controlnet_model", max_length=256, blank=True, null=True)
    controlnet_type = models.CharField("controlnet_type", max_length=256, blank=True, null=True)
    controlnet_conditioning_scale = models.FloatField("Шкала контролнет", blank=True, null=True)
    enhance_style = models.CharField("Дополнительный стиль", max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = "Кастомные настройки для пользователя"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField("Ник telegram аккаунта", unique=True, max_length=32)
    chat_id = models.CharField("id чата с ботом", max_length=64, blank=True, null=True)
    partner_id = models.CharField("id чата для начисления реферальных", max_length=16, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    date_of_payment = models.DateTimeField("Дата платежа", null=True, blank=True)
    date_payment_expired = models.DateTimeField("дата истечения платежа", null=True, blank=True)
    is_active = models.BooleanField("Telegram подтвержден", default=False)
    remain_messages = models.PositiveIntegerField("Оставшиеся генерации", default=10)
    remain_paid_messages = models.PositiveIntegerField("Оставшиеся платные генерации", default=0)
    remain_video_messages = models.PositiveIntegerField("Оставшиеся генерации видео", default=0)
    is_test_user = models.BooleanField("Тестовый пользователь", default=False)
    account = models.ForeignKey(
        DiscordAccount,
        on_delete=models.SET_NULL,
        verbose_name="Discord аккаунт",
        related_name="users",
        blank=True,
        null=True,
    )
    stable_account = models.ForeignKey(
        "stable_messages.StableAccount",
        on_delete=models.SET_NULL,
        verbose_name="Аккаунт stable",
        related_name="stable_users",
        blank=True,
        null=True,
    )
    preset = models.CharField(
        "Суффикс для всех сообщений пользователя",
        max_length=128,
        blank=True,
        null=True
    )
    video_preset = models.CharField(
        "Суффикс для всех видео сообщений пользователя",
        max_length=128,
        blank=True,
        null=True
    )
    style = models.ForeignKey(
        Style,
        on_delete=models.SET_NULL,
        verbose_name="Стиль",
        related_name="users",
        blank=True,
        null=True
    )
    custom_settings = models.ForeignKey(CustomSettings, on_delete=models.SET_NULL, blank=True, null=True)
    used_test_video_payment = models.BooleanField("Оплачивал тестовые генерации", default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username

    @property
    def get_bot_end(self):
        try:
            return self.date_payment_expired.strftime("%d-%m-%Y %H:%M") or "Оплат пока не было(("
        except Exception:
            return "Оплат пока не было(("

    @property
    def all_messages(self):
        if not self.date_payment_expired or self.date_payment_expired < now():
            return self.remain_messages
        return self.remain_messages + self.remain_paid_messages
