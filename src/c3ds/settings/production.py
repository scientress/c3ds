import os
import string

from django.utils.crypto import get_random_string

from .base import *  # NoQa
from .base import env


# SECURITY: Disable debug mode
DEBUG = False

# cookie settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_COOKIE_SECURE = True

# Django compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache.
# See https://docs.djangoproject.com/en/4.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

with suppress(ImportError):
    from .local import *  # NoQa

# SECURITY: Secret Key
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default=None)
if not SECRET_KEY:
    SECRET_FILE = env.path('DJANGO_SECRET_FILE', default=None)
    if SECRET_FILE is None:
        SECRET_FILE = DATA_DIR / '.secret'
    if SECRET_FILE.exists():
        SECRET_KEY = SECRET_FILE.read_text()
    else:
        SECRET_KEY = get_random_string(50, string.printable)
        saved_umask = os.umask(0o177)
        try:
            SECRET_FILE.write_text(SECRET_KEY)
            try:
                os.chown(SECRET_FILE, os.getuid(), os.getgid())
            except AttributeError:
                pass
        finally:
            os.umask(saved_umask)
