from django.db import models
from solo.models import SingletonModel

from stable_messages.choices import StableMessageTypeChoices, StableModels
from users.models import User


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


class StableAccount(models.Model):
    name = models.CharField("Название акка", max_length=256)
    api_key = models.CharField("Ключ доступа к Stable", max_length=256)

    class Meta:
        verbose_name = "Аккаунт в stable "
        verbose_name_plural = "Аккаунты stable"

    def __str__(self):
        return f"Аккаунт {self.name}"


class StableSettings(SingletonModel):
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

    class Meta:
        verbose_name = "Настройки stable"
        verbose_name_plural = verbose_name
