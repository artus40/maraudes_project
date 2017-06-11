from django.utils import timezone as tz

def website_processor(request):
    return {'date': tz.now().date}

