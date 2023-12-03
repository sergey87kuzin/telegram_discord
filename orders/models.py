from django.db import models

from courses.models import Course
from users.models import User


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь"
    )
    total_cost = models.PositiveIntegerField(
        verbose_name="Сумма заказа",
    )
    payment_url = models.CharField(
        verbose_name="Платежная ссылка",
        max_length=1048,
        blank=True,
        null=True
    )
    # срок оплаты бота
    days = models.PositiveIntegerField(
        "Дней для оплаты",
        blank=True,
        null=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Курс",
        blank=True,
        null=True
    )
    payment_status = models.CharField(
        "Статус оплаты",
        choices=(("Not paid", "Не оплачен"), ("Paid", "Оплачен")),
        default="Not paid",
        max_length=15
    )
    created_at = models.DateField(
        "Дата создания",
        auto_now_add=True
    )
    payment_date = models.DateTimeField(
        verbose_name="Время оплаты",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.user.username} от {self.created_at}"
