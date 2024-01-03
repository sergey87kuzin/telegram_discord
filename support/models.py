from django.db import models


class SupportMessage(models.Model):
    telegram_username = models.CharField("Логин телеграм", max_length=256)
    telegram_chat_id = models.CharField("ИД чата телеграм", max_length=128)
    telegram_message_id = models.CharField("ИД сообщения телеграм", max_length=128, blank=True, null=True)
    answer_to_id = models.CharField("ИД сообщения, на которое отвечаем", max_length=128, blank=True, null=True)
    message_text = models.CharField("Текст сообщения", max_length=2048, blank=True, null=True)
    answered = models.BooleanField("Отвечено", default=False)

    class Meta:
        verbose_name = "Сообщение техподдержки"
        verbose_name_plural = "Сообщения техподдержки"

    def __str__(self):
        return self.message_text[:100]
