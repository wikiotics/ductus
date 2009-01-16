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

from ductus.util import iterate_file_object
from ductus.urn import resolve_urn
from urllib2 import urlopen, HTTPError

class RemoteDuctusStorageBackend(object):
    """Fetches resources from a remote Ductus over HTTP"""

    def __init__(self, base_url="http://wikiotics.org"):
        self.__base_url = base_url

    def __remote_url(urn):
        return "%s%s?view=raw" % (self.__base_url, resolve_urn(urn))

    def __contains__(self, key):
        # Remember: if the remote hash is wrong, this backend will claim to
        # "contain" it but will return KeyError on __getitem__.  This certainly
        # goes against expected protocol.  Then again, we could have the
        # function below raise something other can KeyError in this case, since
        # it isn't exactly a normal, expected situation.
        try:
            urlopen(self.__remote_url(key))
        except HTTPError:
            return False
        return True

    def __getitem__(self, key):
        # fixme: check hash.  Do we do it now (read it all into memory), or do
        # it as it is iterated?  Either way, we should have some parameter for
        # the maximum size of a file we will allow.
        try:
            return iterate_file_object(urlopen(self.__remote_url(key)))
        except HTTPError:
            raise KeyError(key)

    def put_file(self, key, tmpfile):
        raise Exception("RemoteDuctusStorageBackend is read-only.")

    def __delitem__(self, key):
        raise Exception("RemoteDuctusStorageBackend is read-only.")

    def __iter__(self):
        raise Exception("Unsupported")

    def __len__(self):
        raise Exception("Unsupported")

# We may also wish to extend this into a new backend that allows http PUT and
# DELETE requests
