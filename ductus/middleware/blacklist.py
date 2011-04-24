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

from socket import inet_aton
from logging import warning

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

class IPAddressBlacklistMiddleware(object):
    def process_request(self, request):
        if request.method == "POST":
            ip = inet_aton(request.remote_addr)
            try:
                banned_ips = file(settings.DUCTUS_BLACKLIST_FILE).read()
            except IOError:
                if settings.DUCTUS_BLACKLIST_STRICT:
                    raise
                else:
                    warning("blacklist file cannot be read")
                    return
            if binary_search(ip, banned_ips):
                return render_to_response("blacklist/blacklisted_ip.html", {
                }, RequestContext(request))

def binary_search(bytematch, bytestring):
    assert isinstance(bytematch, bytes) and isinstance(bytestring, bytes)
    nbytes = len(bytematch)
    if not len(bytestring) % nbytes == 0:
        raise Exception
    nobjects = len(bytestring) // nbytes
    lbound = 0
    rbound = nobjects
    # lbound could be the element, but rbound is one past it
    while lbound != rbound:
        avg = (lbound + rbound) // 2
        getavg = bytestring[avg*nbytes:(avg+1)*nbytes]
        if getavg == bytematch:
            return True
        elif getavg < bytematch:
            lbound = avg + 1
        else:
            rbound = avg
    return False

if __name__ == '__main__':
    all_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    alphabet_subset = ('adefijklmnxz')
    for x in all_alphabet:
        assert binary_search(x, alphabet_subset) == (x in alphabet_subset)

    fourbytestring = sorted(['abcd', 'adfg', 'sdfs', 'gfew', 'dfge'])
    fourbytestring_join = b''.join(fourbytestring)
    strings_to_test = list(fourbytestring) + ['nasw', 'yews']
    for x in strings_to_test:
        assert binary_search(x, fourbytestring_join) == (x in fourbytestring)
