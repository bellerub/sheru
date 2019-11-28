from django.urls import re_path
from sheru import consumers

websocket_urlpatterns = [
  re_path(r'^ws/(?P<cid>[^/]+)$', consumers.CommandConsumer),
]