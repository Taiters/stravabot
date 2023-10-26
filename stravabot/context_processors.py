from django.conf import settings


def context(request):
    return {
        'base_url': settings.BASE_URL,
    }