from django.conf import settings

from courses.models import Course


def headers_courses(request):
    return {"HEADER_COURSES": Course.objects.filter(is_active=True)}


def static_root(request):
    return {"STATIC_ROOT": settings.STATIC_ROOT}
