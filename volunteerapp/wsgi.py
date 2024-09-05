"""
WSGI config for volunteerapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import volunteeringapp.routing  # Import your routing configuration

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteerapp.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),  
    "websocket": AuthMiddlewareStack(
        URLRouter(
            volunteeringapp.routing.websocket_urlpatterns 
        )
    ),
})
