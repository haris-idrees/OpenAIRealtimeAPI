import websocket
import socket
from django.conf import settings


def create_connection_with_ipv4(*args, **kwargs):
    original_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4(host, port, family=socket.AF_INET, *args):
        return original_getaddrinfo(host, port, socket.AF_INET, *args)
    socket.getaddrinfo = getaddrinfo_ipv4
    try:
        return websocket.create_connection(*args, **kwargs)
    finally:
        socket.getaddrinfo = original_getaddrinfo


def connect_to_openai():
    ws = None
    try:
        ws = create_connection_with_ipv4(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',  # Replace with OpenAI WebSocket URL
            header=[
                f'Authorization: Bearer {settings.OPEN_AI_KEY}',
                'OpenAI-Beta: realtime=v1',
                'language: english',
            ]
        )
        print('Connected to OpenAI WebSocket.')
        return ws
    except Exception as e:
        print(f"Error connecting to OpenAI: {e}")
        return None
