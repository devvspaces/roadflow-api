from .base import *  # noqa

ALLOWED_HOSTS = ['roadflow.tripvalue.com.ng']

STATIC_ROOT = BASE_DIR / "static"  # noqa

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=200)  # noqa

PRINT_LOG = False
OFF_EMAIL = False
