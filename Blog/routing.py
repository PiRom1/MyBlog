# monjeu/routing.py
from django.urls import re_path
from Blog.consumers import lobbyConsumer, pongConsumer

websocket_urlpatterns = [
    re_path(r'ws/lobby/(?P<room_name>[^/]+)/(?P<game>[^/]+)/(?P<size>[^/]+)/(?P<type>[^/]+)/$', lobbyConsumer.WaitingRoomConsumer.as_asgi()),
    re_path(r'ws/pong/(?P<room_name>[^/]+)/$', pongConsumer.PongConsumer.as_asgi()),
]
