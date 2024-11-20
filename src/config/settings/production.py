from .staging import *  # noqa

ALLOWED_HOSTS = [config("ALLOWED_HOSTS", default="*")]


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5)  # noqa
}
