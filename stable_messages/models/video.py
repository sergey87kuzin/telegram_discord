from django.db import models

from users.models import User
__all__ = (
    "VideoMessages",
    "SetVideoVariables"
)


class VideoMessages(models.Model):
    telegram_chat_id = models.CharField("Номер чата телеграм", max_length=128)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="video_messages",
        verbose_name="Автор",
    )
    request_id = models.CharField("ID запроса в fireworks", max_length=512, blank=True, null=True)
    initial_image = models.CharField("Картинка-основа", max_length=512, blank=True, null=True)
    video = models.CharField("Сгенерированное видео", max_length=512, blank=True, null=True)
    successfully_generated = models.BooleanField("Успешно сгенерировано", default=False)
    is_sent = models.BooleanField("Отправлено", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    variables = models.CharField("Параметры генерации", max_length=64, blank=True, null=True)
    prompt = models.CharField("Промпт", max_length=2048, blank=True, null=True)
    width = models.CharField("Ширина", max_length=8, blank=True, null=True)
    height = models.CharField("Высота", max_length=8, blank=True, null=True)

    class Meta:
        verbose_name = "Видео сообщение"
        verbose_name_plural = "Видео сообщения"

    def __str__(self):
        return f"Видео сообщение пользователя {self.user.username} от {self.created_at.strftime('mm-DD:HH-MM')}"


class SetVideoVariables(models.Model):
    username = models.CharField("Юзернейм пользователя", max_length=256)
    video_message = models.ForeignKey(
        VideoMessages,
        on_delete=models.CASCADE,
        verbose_name="Сообщение, которому задаем параметры",
        related_name="set_video_variables",
    )
    is_set = models.BooleanField("Уже установлено", default=False)

    class Meta:
        verbose_name = "Заявка на установку формата сообщения"
        verbose_name_plural = "Заявки на установку формата сообщения"

    def __str__(self):
        return f"Заявка пользователя {self.username} на изменение формата сообщения {self.video_message.id}"
