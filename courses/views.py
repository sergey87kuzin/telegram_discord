from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F, Value, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import ListView

from courses.models import Course, UserCourses, Lesson


class CoursesListView(ListView):
    queryset = Course.objects.filter(is_active=True)
    context_object_name = "courses"
    template_name = "courses_list.html"


class UserCoursesListView(ListView):
    queryset = Course.objects.filter(is_active=True)
    context_object_name = "courses"
    template_name = "courses_list.html"

    def get_queryset(self):
        user_courses = list(UserCourses.objects.filter(
            user=self.request.user,
            course__is_active=True,
            expires_at__gte=now()
        ).values_list("id", flat=True))
        return Course.objects.filter(id__in=user_courses)


@login_required
def open_next_lesson(request, course_id, lesson_id):
    user_course = UserCourses.objects.filter(
        user=request.user, course_id=course_id
    ).first()
    if lesson_id not in user_course.finished_lessons:
        user_course.finished_lessons.append(lesson_id)
        user_course.save()
    return redirect(reverse("courses:single_course", kwargs={"course_id": course_id}))


class CourseView(ListView):
    context_object_name = "lessons"
    template_name = "course.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and UserCourses.objects.filter(
            id=self.kwargs.get("course_id"),
            user=user
        ):
            user_course = UserCourses.objects.filter(
                user=self.request.user,
                course_id=self.kwargs.get("course_id"),
                expires_at__gte=now()
            ).first()
            finished_lessons = user_course.finished_lessons if user_course else []
            return Lesson.objects.filter(
                course_id=self.kwargs.get("course_id"),
                is_active=True,
            ).filter(
                Q(is_free=True) | Q(previous_lesson_id__in=finished_lessons)
            ).order_by("order", "id").distinct()
        return Lesson.objects.filter(
            course_id=self.kwargs.get("course_id"),
            is_active=True,
            is_free=True
        ).order_by("order", "id").distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        course = Course.objects.filter(id=self.kwargs.get("course_id")).first()
        user = self.request.user
        context["has_course"] = False
        context["course_name"] = course.name
        context["course_cover"] = course.cover
        context["course_id"] = course.id
        if user and UserCourses.objects.filter(
                course=course, user=user, buying_date__gte=now() - timedelta(days=course.duration)
        ).exists():
            context["has_course"] = True
        return context
