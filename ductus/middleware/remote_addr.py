# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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

from django.conf import settings

class RemoteAddrMiddleware(object):
    """Sets request.remote_addr, taking into account proxy servers

    DUCTUS_TRUSTED_PROXY_SERVERS should be a tuple of IP addresses.  We must be
    able to trust all incoming requests from these IP addresses in the sense
    that they do not spoof the X-Forwarded-For header.
    """

    def __init__(self, trusted_proxy_servers=None):
        if trusted_proxy_servers is None:
            trusted_proxy_servers = getattr(settings, "DUCTUS_TRUSTED_PROXY_SERVERS", ())
        self.trusted_proxy_servers = frozenset(trusted_proxy_servers)

    def process_request(self, request):
        remote_addr = request.META["REMOTE_ADDR"]

        if "HTTP_X_FORWARDED_FOR" in request.META:
            remote_addrs = request.META["HTTP_X_FORWARDED_FOR"].split(',')
            remote_addrs = [a.strip() for a in remote_addrs]
            try:
                while remote_addr in self.trusted_proxy_servers:
                    remote_addr = remote_addrs.pop()
            except IndexError:
                pass

        request.remote_addr = remote_addr
