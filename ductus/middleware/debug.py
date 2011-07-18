# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    def process_response(self, request, response):
        if request.is_ajax():
            if response.status_code in (400, 403):
                logger.error(response.content)
        return response
