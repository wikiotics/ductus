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

import re

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.core.validators import ipv4_re
from django.http import HttpResponseRedirect
from django.utils.ipv6 import is_valid_ipv6_address

CANONICAL_HOSTNAME = getattr(settings, "CANONICAL_HOSTNAME", None)

ipv6_possible_re = re.compile(r'^\[(.+)\](:\d+)?$')

def host_represents_ip_address(host):
    """
    Returns True if the host represents an IP address, possibly with a port
    number

    >>> host_represents_ip_address('example.com')
    False
    >>> host_represents_ip_address('10.0.0.1')
    True
    >>> host_represents_ip_address('10.0.0.1:80')
    True
    >>> host_represents_ip_address('[2001:db8:85a3:8d3:1319:8a2e:370:7348]')
    True
    >>> host_represents_ip_address('[2001:db8:85a3:8d3:1319:8a2e:370::::7348]')
    False
    >>> host_represents_ip_address('[2001:db8:85a3:8d3:1319:8a2e:370:7348]:')
    False
    >>> host_represents_ip_address('[2001:db8:85a3:8d3:1319:8a2e:370:7348]:443')
    True
    """
    host_split = host.split(':')
    if len(host_split) <= 2:
        # it might be an ipv4 address with optional port number
        if ipv4_re.match(host_split[0]):
            return True
    else:
        # it might be an ipv6 address
        match = ipv6_possible_re.match(host)
        if match and is_valid_ipv6_address(match.group(1)):
            return True
    return False

class CanonicalHostnameMiddleware(object):
    """If CANONICAL_HOSTNAME is given, always make sure the url points to that server
    (and redirect if it doesn't)
    """

    def __init__(self):
        if not CANONICAL_HOSTNAME:
            raise MiddlewareNotUsed

    def process_request(self, request):
        # it's possible that HTTP_HOST may not be set for HTTP/1.0 requests
        if 'HTTP_HOST' not in request.META:
            return

        host = request.META['HTTP_HOST']
        if host == CANONICAL_HOSTNAME or request.method in ('POST', 'PUT'):
            return

        # if somebody requested an ip address, let that be
        if host_represents_ip_address(host):
            return

        proto = 'https' if request.is_secure() else 'http'
        new_url = "%s://%s%s" % (proto, CANONICAL_HOSTNAME, request.path)
        if request.META['QUERY_STRING']:
            new_url += '?' + request.META['QUERY_STRING']
        return HttpResponseRedirect(new_url)
