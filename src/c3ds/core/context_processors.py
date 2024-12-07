from django.conf import settings


def event_data(request):
    return {'event': {
        'day_zero': settings.DAY_ZERO.isoformat(),
    }}