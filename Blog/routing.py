# monjeu/routing.py
from django.urls import re_path
from Blog.consumers import lobbyConsumer, pongConsumer

websocket_urlpatterns = [
    re_path(r'ws/lobby/(?P<room_name>[^/]+)/(?P<game>[^/]+)/(?P<size>[^/]+)/$', lobbyConsumer.WaitingRoomConsumer.as_asgi()),
    re_path(r'ws/jeux/pong/(?P<room_name>[^/]+)/(?P<token>[^/]+)/$', pongConsumer.PongConsumer.as_asgi()),
]
