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
    say_hi_video = models.FileField("Приветственное видео", blank=True, null=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = verbose_name
