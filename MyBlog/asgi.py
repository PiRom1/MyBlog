"""
ASGI config for MyBlog project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# asgi.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')
import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # Added for authentication
from channels.security.websocket import AllowedHostsOriginValidator
import Blog.routing  # votre fichier de routage pour les websockets

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(  # Wrap the URLRouter with AuthMiddlewareStack
            URLRouter(
                Blog.routing.websocket_urlpatterns
            )
        ),
    ),
})
