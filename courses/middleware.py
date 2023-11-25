from django.conf import settings


class RefererHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        referer = request.META.get('HTTP_REFERER', None)
        response = self.get_response(request)
        response["HTTP_REFERER"] = settings.SITE_DOMAIN
        return response
