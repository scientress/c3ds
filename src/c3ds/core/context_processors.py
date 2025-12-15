from django.conf import settings


def event_data(request):
    return {'event': {
        'day_zero': settings.DAY_ZERO.isoformat(),
    }}

def extra_data(request):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()

    return {'extra_data': {
        'ip_address': ip_address,
    }}