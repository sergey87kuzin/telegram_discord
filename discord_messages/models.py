from django.db import models

from discord_messages.choices import DiscordTypes


class Message(models.Model):
    text = models.CharField("Текст сообщения", max_length=1024)
    eng_text = models.CharField("Текст сообщения английский", max_length=1024, blank=True, null=True)
    # при отправке сида текст сообщения дискордом режется по двойному дефису
    no_ar_text = models.CharField("Текст сообщения без дефисов", max_length=1024, blank=True, null=True)
    user_telegram = models.CharField("Телега пользователя", max_length=128)
    telegram_id = models.CharField("id telegram пользователя", max_length=64)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Пользователь",
    )
    discord_message_id = models.CharField(
        "Номер сообщения в discord", max_length=64, blank=True, null=True
    )
    images = models.CharField(
        "Список url вложенных файлов", max_length=2048, blank=True, null=True
    )
    buttons = models.JSONField("Коды кнопок ответа", default=dict)
    answer_type = models.CharField(
        "Тип ответа в discord", choices=DiscordTypes.CHOICES, default="start_gen", max_length=64
    )
    answer_sent = models.BooleanField("Ответ отправлен", default=False)
    seed = models.CharField("Сид картинки", max_length=128, blank=True, null=True)
    job = models.CharField("JOB сообщения", max_length=128, blank=True, null=True)
    seed_send = models.BooleanField("Сид получен и отправлен", default=False)
    created_at = models.DateTimeField("Создано:", auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.text} от {self.user_telegram}"


class ConfirmMessage(models.Model):
    code = models.CharField("Код подтверждения", max_length=16)
    telegram_nick = models.CharField("Ник telegram", max_length=256)
    used = models.BooleanField("Использован", default=False)
    new_message_sent = models.BooleanField("Отправлено новое сообщение", default=False)

    class Meta:
        verbose_name = "Сообщение с кодом"
        verbose_name_plural = "Сообщения с кодом"

    def __str__(self):
        return f"Сообщение {self.telegram_nick} с кодом {self.code}"


class DiscordAccount(models.Model):
    login = models.CharField("login", max_length=128)
    password = models.CharField("password", max_length=256)
    session_id = models.CharField("session_id", max_length=128, blank=True, null=True)
    channel_id = models.CharField("channel_id", max_length=128, blank=True, null=True)
    queue_delay = models.PositiveIntegerField("Задержка в отправке сообщений", default=1)
    last_message_id = models.CharField(
        "ID последнего запрошенного сообщения в акке", max_length=128, blank=True, null=True
    )
    queue_number = models.PositiveIntegerField("Номер очереди", default=1)

    class Meta:
        verbose_name = "Аккаунт дискорд для подключения midjourney"
        verbose_name_plural = "Аккаунты дискорд для подключения midjourney"

    def __str__(self):
        return f"Аккаунт {self.login}"


class DiscordConnection(models.Model):
    account = models.ForeignKey(
        DiscordAccount,
        on_delete=models.CASCADE,
        verbose_name="Соединение с дискордом",
        related_name="connections"
    )
    token = models.CharField("token", max_length=256, blank=True, null=True)
    channel_id = models.CharField("Номер канала", max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = "Соединение с discord"
        verbose_name_plural = "Соединения с discord"

    def __str__(self):
        return f"Соединение {self.account.login}"
