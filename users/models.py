from django.contrib.auth.models import AbstractUser
from django.db import models

from discord_messages.models import DiscordAccount
from users.managers import CustomUserManager


class User(AbstractUser):
    username = models.CharField("Ник telegram аккаунта", unique=True, max_length=32)
    chat_id = models.CharField("id чата с ботом", max_length=64, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    date_of_payment = models.DateTimeField("Дата платежа", null=True, blank=True)
    date_payment_expired = models.DateTimeField("дата истечения платежа", null=True, blank=True)
    is_active = models.BooleanField("Telegram подтвержден", default=False)
    remain_messages = models.PositiveIntegerField("Оставшиеся генерации", default=0)
    account = models.ForeignKey(
        DiscordAccount,
        on_delete=models.SET_NULL,
        verbose_name="Discord аккаунт",
        related_name="users",
        blank=True,
        null=True,
    )
    preset = models.CharField(
        "Суффикс для всех сообщений пользователя",
        max_length=128,
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
