from django.conf import settings


class RefererHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["HTTP_HEADER"] = settings.SITE_DOMAIN
        return response
