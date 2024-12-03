import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Applications.Order import consumers
from django.urls import path


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DriveThruChannels.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/audio/', consumers.Socket1Consumer.as_asgi()),  # Frontend WebSocket
        ])
    ),
})
