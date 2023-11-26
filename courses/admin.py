from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from courses.models import Course, Lesson, UserCourses, LessonTextBlock


class LessonTextBlockAdminForm(forms.ModelForm):

    class Meta:
        model = LessonTextBlock
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget = CKEditorUploadingWidget()


@admin.register(LessonTextBlock)
class LessonTextBlockAdmin(admin.ModelAdmin):
    list_display = ["lesson", "text", "order", "is_active"]
    search_fields = ["lesson__name", "text"]
    list_filter = ["lesson__name", "is_active"]
    form = LessonTextBlockAdminForm


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "name",
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
    list_display = (
        "user",
        "course",
        "buying_date",
        "expires_at"
    )
