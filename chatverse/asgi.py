import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatverse.settings')

# Setup Django BEFORE importing anything that depends on settings/models
django.setup()

import whispr.routing  # Safe to import after django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            whispr.routing.websocket_urlpatterns
        )
    ),
})
