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

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

logger = logging.getLogger(__name__)

class UpstreamSslProxyMiddleware(object):
    """Sets request.is_secure() according to the X-Forwarded-Proto header

    This middleware only goes into effect if DUCTUS_TRUST_X_FORWARDED_PROTO is
    explicitly set to be True.

    Only enable this setting if Ductus is being served behind a trusted proxy
    that sets the X-Forwarded-Proto header.
    """

    def __init__(self, trusted_proxy_servers=None):
        if not getattr(settings, "DUCTUS_TRUST_X_FORWARDED_PROTO", False):
            raise MiddlewareNotUsed

    def process_request(self, request):
        try:
            proto = request.META['HTTP_X_FORWARDED_PROTO']
        except KeyError:
            logger.error("X-Forwarded-Proto is not being set appropriately by your upstream proxy.  You should set `DUCTUS_TRUST_X_FORWARDED_PROTO = False` until this is fixed.  Otherwise, any user will be able trick Ductus into thinking it is serving a secure page.")
            raise

        try:
            is_secure = {'http': False, 'https': True}[proto]
        except KeyError:
            logger.error("X-Forwarded-Proto contains a value other than http[s]: `%s`" % proto)
            raise

        request.is_secure = lambda: is_secure
