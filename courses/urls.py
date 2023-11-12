from django.urls import path

from courses.views import CoursesListView, UserCoursesListView, CourseView, open_next_lesson

app_name = "courses"

urlpatterns = [
    path("all_courses/", CoursesListView.as_view(), name="full_list"),
    path("user_courses/", UserCoursesListView.as_view(), name="user_list"),
    path("course/<int:course_id>/", CourseView.as_view(), name="single_course"),
    path("<int:course_id>/<int:lesson_id>/open_lesson/", open_next_lesson, name="open_lesson")
]
