from django.contrib.auth.middleware import PersistentRemoteUserMiddleware

# Use Custom Remote Header
class WebAuthHeaderMiddleware(PersistentRemoteUserMiddleware):
    header = 'HTTP_X_REMOTE_USER'
