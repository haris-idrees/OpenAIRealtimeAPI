from django.urls import re_path
from .consumers import Socket1Consumer

websocket_urlpatterns = [
    re_path(r'^ws/audio/$', Socket1Consumer.as_asgi()),
]
