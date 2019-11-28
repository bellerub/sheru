from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import sheru.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
    URLRouter(
      sheru.routing.websocket_urlpatterns
    )
  ),
})