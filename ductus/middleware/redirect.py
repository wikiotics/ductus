from django.conf import settings
from django.shortcuts import redirect

REDIRECT_TABLE = getattr(settings, "REDIRECT_TABLE", None)

class RedirectMiddleware(object):
    "Redirect matching requests based on settings.REDIRECT_TABLE if given"

    def __init__(self):
        if not REDIRECT_TABLE:
            raise MiddlewareNotUsed

    def process_request(self, request):
        if request.path in REDIRECT_TABLE:
            return redirect(REDIRECT_TABLE[request.path])
