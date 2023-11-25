from courses.models import Course


def headers_courses(request):
    return {"HEADER_COURSES": Course.objects.filter(is_active=True)}
