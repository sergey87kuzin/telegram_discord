from django.contrib.auth.models import AbstractUser
from django.db import models

from discord_messages.models import DiscordAccount
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


class User(AbstractUser):
    username = models.CharField("Ник telegram аккаунта", unique=True, max_length=32)
    chat_id = models.CharField("id чата с ботом", max_length=64, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    date_of_payment = models.DateTimeField("Дата платежа", null=True, blank=True)
    date_payment_expired = models.DateTimeField("дата истечения платежа", null=True, blank=True)
    is_active = models.BooleanField("Telegram подтвержден", default=False)
    remain_messages = models.PositiveIntegerField("Оставшиеся генерации", default=10)
    remain_paid_messages = models.PositiveIntegerField("Оставшиеся платные генерации", default=0)
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
    style = models.ForeignKey(
        Style,
        on_delete=models.SET_NULL,
        verbose_name="Стиль",
        related_name="users",
        blank=True,
        null=True
    )
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
        return self.remain_messages + self.remain_paid_messages
