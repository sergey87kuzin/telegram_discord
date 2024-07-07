from django.db import models

from stable_messages.choices import StableMessageTypeChoices
from users.models import User
__all__ = (
    "StableMessage",
)


class StableMessage(models.Model):
    initial_text = models.CharField("Начальный текст", max_length=2048)
    eng_text = models.CharField("Переведенный текст", max_length=2048)
    telegram_chat_id = models.CharField("Номер чата телеграм", max_length=128)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stable_messages",
        verbose_name="Автор",
    )
    stable_request_id = models.CharField("ID запроса в stable", max_length=512, blank=True, null=True)
    single_image = models.CharField("Общая картинка", max_length=1024, blank=True, null=True)
    first_image = models.CharField("Первая картинка", max_length=1024, blank=True, null=True)
    second_image = models.CharField("Вторая картинка", max_length=1024, blank=True, null=True)
    third_image = models.CharField("Третья картинка", max_length=1024, blank=True, null=True)
    fourth_image = models.CharField("Четвертая картинка", max_length=1024, blank=True, null=True)
    answer_sent = models.BooleanField("Ответ отправлен", default=False)
    sent_to_stable = models.BooleanField("Запрос на генерацию отправлен", default=True)
    width = models.CharField("Ширина", max_length=8, blank=True, null=True)
    height = models.CharField("Высота", max_length=8, blank=True, null=True)
    seed = models.CharField("Сид", max_length=16, blank=True, null=True)
    created_at = models.DateTimeField("Создан в", auto_now_add=True)
    message_type = models.CharField(
        "Тип сообщения",
        max_length=128,
        choices=StableMessageTypeChoices.CHOICES,
        default=StableMessageTypeChoices.FIRST
    )
    new_endpoint = models.BooleanField("Новый сервис", default=False)

    class Meta:
        verbose_name = "Сообщение в stable"
        verbose_name_plural = "Сообщения в stable"

    def __str__(self):
        return self.eng_text
