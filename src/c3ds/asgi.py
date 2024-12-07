"""
ASGI config for c3ds project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from contextlib import suppress

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c3ds.settings.production')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
})

# optional support for static files via starlette
with suppress(ImportError):
    # settings need to be loaded after django init via get_asgi_application
    from django.conf import settings
    from starlette.applications import Starlette
    from starlette.routing import Mount
    from starlette.staticfiles import StaticFiles

    static_app = ProtocolTypeRouter({
        "http": Starlette(routes=[
            Mount(
                path=settings.STATIC_URL,
                app=StaticFiles(directory=settings.STATIC_ROOT, follow_symlink=True),
                name='static',
            ),
            Mount(
                path=settings.MEDIA_URL,
                app=StaticFiles(directory=settings.MEDIA_ROOT, follow_symlink=True),
                name='media',
            ),
            Mount(path='/', app=django_asgi_app),
        ]),
    })
