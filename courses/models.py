from datetime import timedelta

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils.timezone import now

from users.models import User


from ckeditor.fields import RichTextField


class Course(models.Model):
    name = models.CharField("Название курса", max_length=256)
    cover = models.FileField("Обложка курса")
    cost = models.PositiveIntegerField("Стоимость курса")
    duration = models.PositiveIntegerField("Продолжительность курса, дней")
    is_active = models.BooleanField(
        "Активный", default=False
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ("-id",)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="lessons"
    )
    name = models.CharField(
        "Название урока",
        max_length=256
    )
    description = RichTextField("Описание урока", blank=True)
    cover = models.FileField("Обложка урока")
    cover_blocked = models.ImageField("Обложка заблокированная", blank=True, null=True)
    is_free = models.BooleanField(
        "Бесплатный",
        default=False
    )
    video_url = models.CharField(
        "Источник видео",
        max_length=1024,
        blank=True,
        null=True
    )
    previous_lesson = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="Предыдущий урок",
        related_name="next_lessons",
        blank=True,
        null=True
    )
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок", default=1)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("course_id",)

    def __str__(self):
        return f"Урок {self.name} курса {self.course.name}"


class LessonTextBlock(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name="Урок",
    )
    image = models.ImageField("Картинка")
    text = RichTextUploadingField("Текст к картинке", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=1)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Блок урока"
        verbose_name_plural = "Блоки уроков"
        ordering = ("order",)


class UserCourses(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name="Курс"
    )
    buying_date = models.DateField(
        verbose_name="Дата покупки",
        auto_now_add=False,
    )
    expires_at = models.DateField(
        verbose_name="Дата окончания",
        auto_now_add=False,
    )
    finished_lessons = models.JSONField(
        "Пройденные уроки",
        default=list,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Курс пользователей"
        verbose_name_plural = "Курсы пользователей"

    def __str__(self):
        return f"Курс {self.course.name} пользователя {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.buying_date = now()
        self.expires_at = self.buying_date + timedelta(days=self.course.duration)
        super().save(*args, **kwargs)

    # @property
    # def expires_at(self):
    #     return self.buying_date + timedelta(days=self.course.duration)
