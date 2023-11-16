from django.contrib import admin

from courses.models import Course, Lesson, UserCourses


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
