# flake8: noqa

from .dev import *

SECRET_KEY = "fake-key"

INSTALLED_APPS += [
    "tests"
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test.db.sqlite3',
    },
}

TEST_DB_USER = config("TEST_DB_USER", default="")

if TEST_DB_USER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': "trip_testing_fake_db",
            'USER': TEST_DB_USER,
            'PASSWORD': config("TEST_DB_PASSWORD"),
            'HOST': 'localhost',
            'PORT': '',
        }
    }


# use default loc mem cache for tests
CACHES['default']["BACKEND"] = 'django.core.cache.backends.locmem.LocMemCache'
