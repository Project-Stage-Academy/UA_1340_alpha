from .consumers import ChatConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
]
