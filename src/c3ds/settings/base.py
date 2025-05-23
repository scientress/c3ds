"""
Django settings for c3ds project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import datetime
from contextlib import suppress
from pathlib import Path

from django.contrib.messages import constants as messages

from c3ds.utils.environ import Env

env = Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent
DATA_DIR = env.path('C3DS_DATA_DIR', default=BASE_DIR / 'data')
MEDIA_ROOT = env.path('C3DS_MEDIA_ROOT', default=DATA_DIR / 'media')
STATIC_ROOT = env.path('C3DS_STATIC_ROOT', PROJECT_DIR / 'static.dist')

ALLOWED_HOSTS = env.list('C3DS_ALLOWED_HOSTS', default=['*'])

# Application definition

INSTALLED_APPS = [
    'c3ds.core',
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'compressor',
    'ninja',
    'django_vite_plugin',
    'social_django',
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

with suppress(ImportError):
    import django_extensions  # noqa
    INSTALLED_APPS.append('django_extensions')


ROOT_URLCONF = 'c3ds.urls'


# Template settings

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
                'c3ds.core.context_processors.event_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'c3ds.wsgi.application'
ASGI_APPLICATION = 'c3ds.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

_db_backend = env.str('C3DS_DATABASE_BACKEND', default='sqlite3')
DATABASES: dict[str, dict[str, str | int | Path]] = {
    'default': env.db_url('C3DS_DATABASE') if 'C3DS_DATABASE' in env else {
        'ENGINE': _db_backend if '.' in _db_backend else 'django.db.backends.' + _db_backend,
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}
DATABASES['default'].setdefault('CONN_MAX_AGE',
                                env.int('C3DS_DATABASE_CONN_MAX_AGE',
                                        default=(0 if _db_backend.endswith('sqlite3') else 120)))
DATABASES['default'].setdefault('CONN_HEALTH_CHECKS', not DATABASES['default']['ENGINE'].endswith('sqlite3'))


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Cookies

SESSION_COOKIE_NAME = 'c3ds_session'
SESSION_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_NAME = 'c3ds_language'
CSRF_COOKIE_NAME = 'c3ds_csrftoken'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = env.str('C3DS_STATIC_URL', default='/static/')
MEDIA_URL = env.str('C3DS_MEDIA_URL', default='/media/')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = [
    PROJECT_DIR / "static",
]

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_ENABLED = COMPRESS_OFFLINE = False

COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSCompressorFilter',
)

COMPRESS_CSS_HASHING_METHOD = 'content'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USER_REGISTRATION = env.bool('C3DS_USER_REGISTRATION', default=False)

INTERNAL_IPS = ('127.0.0.1', '::1')

MESSAGE_TAGS = {
    messages.INFO: 'alert-info',
    messages.ERROR: 'alert-danger',
    messages.WARNING: 'alert-warning',
    messages.SUCCESS: 'alert-success',
}
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

SILENCED_SYSTEM_CHECKS = ['debug_toolbar.W006']


# EMAIL SETTINGS

MAIL_FROM = SERVER_EMAIL = DEFAULT_FROM_EMAIL = env.str('C3DS_EMAIL_FROM', default='c3ds@localhost')
EMAIL_HOST = env.str('C3DS_EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('C3DS_EMAIL_PORT', default=25)
EMAIL_HOST_USER = env.str('C3DS_EMAIL_USER', default='')
EMAIL_HOST_PASSWORD = env.str('C3DS_EMAIL_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('C3DS_EMAIL_TLS', default=False)
EMAIL_USE_SSL = env.bool('C3DS_EMAIL_SSL', default=False)
EMAIL_BACKEND = env.str(
    'C3DS_EMAIL_BACKEND',
    default='django.core.mail.backends.' + ('console' if EMAIL_HOST == 'localhost' else 'smtp') + '.EmailBackend'
)
if 'C3DS_EMAIL' in env:
    vars().update(env.email_url('C3DS_EMAIL'))
EMAIL_SUBJECT_PREFIX = env.str('C3DS_SUBJECT_PREFIX', '[c3ds]')

ADMINS = [('Admin', n) for n in env.list('C3DS_ADMINS', default=[])]


# Cache and session storage

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
HAS_REAL_CACHE = False

HAS_REDIS = bool(env.str('C3DS_REDIS', default=None))
REDIS_CONNECTION_POOL = None
if HAS_REDIS:
    import redis
    HAS_REAL_CACHE = True
    REDIS_SERVERS = env.list('C3DS_REDIS')
    CACHES['default'] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_SERVERS,
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    REDIS_CONNECTION_POOL = redis.ConnectionPool.from_url(REDIS_SERVERS[0])


# Django Channels

if HAS_REDIS:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": REDIS_SERVERS,
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }


# Celery

HAS_CELERY = bool(env.str('C3DS_CELERY_BROKER', default=None))
if HAS_CELERY:
    BROKER_URL = env.str('C3DS_CELERY_BROKER')
    CELERY_RESULT_BACKEND = env.str('C3DS_CELERY_BACKEND')
    CELERY_SEND_TASK_ERROR_EMAILS = bool(ADMINS)
else:
    CELERY_ALWAYS_EAGER = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'


# Event Config
DAY_ZERO = env.str('C3DS_DAY_ZERO', default=None)
if DAY_ZERO:
    DAY_ZERO = datetime.datetime.fromisoformat(DAY_ZERO)


# SSO
SOCIAL_AUTH_PIPELINE = (
    ###################
    # Default pipelines
    ###################

    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',


    ###################
    # Custom pipelines
    ###################
    # Make Superuser
    'c3ds.core.sso.make_superuser',
)
