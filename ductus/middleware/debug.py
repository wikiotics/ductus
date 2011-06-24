import logging
import sys
import traceback

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

logger = logging.getLogger(__name__)

class DuctusDebugMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed

    def process_exception(self, request, exception):
        "Log AJAX exceptions"

        if request.is_ajax():
            exc_type, exc_info, tb = sys.exc_info()
            msg = list(traceback.format_tb(tb))
            msg.append(exc_type.__name__)
            msg.append(repr(exc_info))
            logger.error("\n".join(msg))
