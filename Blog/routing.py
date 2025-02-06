# monjeu/routing.py
from django.urls import re_path
from Blog.consumers import TOWConsumer, lobbyConsumer

websocket_urlpatterns = [
    re_path(r'ws/tiracorde/$', TOWConsumer.TugOfWarConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<room_name>[^/]+)/(?P<game>[^/]+)/(?P<size>[^/]+)/$', lobbyConsumer.WaitingRoomConsumer.as_asgi()),
]
