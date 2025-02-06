# monjeu/routing.py
from django.urls import re_path
from Blog.consumers import TOWConsumer, lobbyConsumer

websocket_urlpatterns = [
    re_path(r'ws/tiracorde/$', TOWConsumer.TugOfWarConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<room_name>[^/]+)/$', lobbyConsumer.WaitingRoomConsumer.as_asgi()),  # added lobby routing with room_name
]
