from datetime import timedelta
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
ENCRYPTING_KEY = config('ENCRYPTING_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    "corsheaders",

    'account',
    'Curriculum',
    'Feedback',
    'Quiz',
    'Resource',
    'RoadMap',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'utils.base.permissions.IsAuthenticated',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS': 'utils.base.pagination.CustomPagination',

    'DEFAULT_RENDERER_CLASSES': (
        'utils.base.renderer.ApiRenderer',
    ),
}

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utils.base.schema.BaseSchema',
    "SECURITY_DEFINITIONS": {
        "JWT [Bearer {TOKEN}]": {
            "name": "Authorization",
            "type": "apiKey",
            "in": "header",
        },
        "Basic": {
            "type": "basic",
            "name": "Authorization",
        }
    },
    "USE_SESSION_AUTH": False,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'account.User'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]


REDIS_LOCATION = config("REDIS_LOCATION", default="")

if REDIS_LOCATION:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_LOCATION,
        }
    }


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DB_NAME = config("DB_NAME", default='')

if DB_NAME:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': DB_NAME,
            'USER': config("DB_USER", default=''),
            'PASSWORD': config("DB_PASSWORD", default=''),
            'HOST': 'localhost',
        }
    }


STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = '/media/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'basic': {
            'handlers': ['basic_h'],
            'level': 'DEBUG',
        },
        'basic.error': {
            'handlers': ['basic_e'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'handlers': {
        'basic_h': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'formatter': 'simple',
        },
        'basic_e': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/error.log',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'simple': {
            'format': '{levelname} : {asctime} : {message}',
            'style': '{',
        }
    }
}


PASSWORD_RESET_TIMEOUT = 600


# Emails settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@trip.dev')


# Remember to change to 5mins
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=200),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

MAX_STORE_IMAGE = 6

ALLOWED_IMAGE_EXTS = ['jpeg', 'jpg', 'png']

PRINT_LOG = True
OFF_EMAIL = True

MAX_IMAGE_UPLOAD_SIZE = 2621440  # 2.5MB

APP_NAME = 'RoadFlow'

USERNAME_PREFIX = 'roadflow'

SECRET_LENGTH_START = 32
SECRET_LENGTH_STOP = 64

OTP_CACHE_TIMEOUT = 30 * 60  # 30 minutes
DEFAULT_OTP = "123456"

TEST_INTERVAL_SECONDS = 10 # 1 * 24 * 60 * 60

MINDSDB_SERVER_USERNAME = config("MINDSDB_SERVER_USERNAME")
MINDSDB_SERVER_PASSWORD = config("MINDSDB_SERVER_PASSWORD")

SHOWWCASE_API_KEY = config("SHOWWCASE_API_KEY")
SHOWWCASE_BASE_URL = "https://cache.showwcase.com"
SHOWWCASE_API_CACHE_TIME = 60 * 60 * 2  # 2 hours
