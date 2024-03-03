from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from bot_config.models import SiteSettings
from courses.models import Course, Lesson, UserCourses, LessonTextBlock, Review, Prolongation
from discord_messages.telegram_helper import bot


class LessonTextBlockAdminForm(forms.ModelForm):

    class Meta:
        model = LessonTextBlock
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget = CKEditorUploadingWidget()


@admin.register(LessonTextBlock)
class LessonTextBlockAdmin(admin.ModelAdmin):
    list_display = ["lesson", "order", "is_active", "text"]
    search_fields = ["lesson__name", "text"]
    list_filter = ["lesson__name", "is_active"]
    form = LessonTextBlockAdminForm


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Prolongation)
class ProlongationAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "course",
        "description",
        "cover",
    )
    fields = (
        "course",
        "name",
        "description",
        "cover",
        "cover_blocked",
        "is_free",
        "video_url",
        "previous_lesson",
        "order",
        "is_active"
    )


@admin.register(UserCourses)
class UserCoursesAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "user",
        "course",
        "buying_date",
        "expires_at",
    )
    actions = ["send_message"]

    def send_message(self, request, queryset):
        site_settings = SiteSettings.get_solo()
        for course in queryset:
            if course.user.chat_id:
                try:
                    bot.send_message(
                        chat_id=course.user.chat_id,
                        text=site_settings.notice_message
                    )
                except Exception:
                    pass

    send_message.short_description = "Отправить сообщение"
