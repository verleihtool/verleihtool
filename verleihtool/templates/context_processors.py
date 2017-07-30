from django.conf import settings


def template_settings(request):
    return {
        'PRIVACY_URL': settings.PRIVACY_URL,
        'IMPRINT_URL': settings.IMPRINT_URL,
        'GITHUB_URL': settings.GITHUB_URL,
    }
