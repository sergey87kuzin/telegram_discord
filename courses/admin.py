from django.contrib import admin

from courses.models import Course, Lesson, UserCourses


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(UserCourses)
class UserCoursesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "buying_date",
        "expires_at"
    )
