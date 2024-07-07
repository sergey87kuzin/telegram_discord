from django.db import models
from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    day_tariff_cost = models.PositiveIntegerField(
        "Стоимость дневной подписки",
        default=150
    )
    month_tariff_cost = models.PositiveIntegerField(
        "Стоимость месячной подписки",
        default=1000
    )
    day_tariff_count = models.PositiveIntegerField(
        "Количество генераций при покупке бота на день",
        default=50
    )
    month_tariff_count = models.PositiveIntegerField(
        "Количество генераций при покупке бота на месяц",
        default=1000
    )
    say_hi_video = models.FileField("Приветственное видео", blank=True, null=True)
    notice_message = models.CharField(
        "Сообщение для отправки пользователям",
        blank=True,
        null=True,
        max_length=512
    )
    say_hi_video_video_bot = models.FileField("Приветственное видео для видео бота", blank=True, null=True)
    settings_lesson_link = models.CharField("Ссылка на урок по настройкам", max_length=1024, blank=True, null=True)
    queue_number = models.PositiveIntegerField("Номер очереди для отправки сообщений", default=0)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = verbose_name


class Notice(models.Model):
    text = models.CharField("Текст уведомления", max_length=1024)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return self.text
