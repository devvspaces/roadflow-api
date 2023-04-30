from datetime import datetime

from django.conf import settings
import pytz


def dt_now():
    """
    Get a timezone aware datetime
    """
    timezone = pytz.timezone(settings.TIME_ZONE)
    return timezone.localize(datetime.now())
