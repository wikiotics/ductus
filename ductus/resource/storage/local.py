# Ductus
# Copyright (C) 2008  Jim Garrison <jim@garrison.cc>
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

import os, os.path
from shutil import copyfile

from ductus.urn import UnsupportedURN
from ductus.util import iterate_file, sequence_contains_only

class LocalStorageBackend(object):
    """Local storage backend.

    This backend supports only Class-A URN's (as defined in ductus.urn).
    """

    def __init__(self, storage_directory):
        self.__storage_directory = storage_directory

    def __storage_location(self, urn):
        hash_type, digest = split_urn(urn)
        return os.path.join(self.__storage_directory, hash_type,
                            digest[0:2], (digest[2:4] or digest[0:2]), digest)

    def __storage_location_else_keyerror(self, urn):
        try:
            return self.__storage_location(urn)
        except UnsupportedURN:
            raise KeyError(urn)

    def __contains__(self, key):
        # does file exist, and can we read it?
        return os.access(self.__storage_location_else_keyerror(key), os.R_OK)

    def put_file(self, key, tmpfile):
        pathname = self.__storage_location(key)

        if os.path.exists(pathname):
            # Compare the files
            f1 = file(pathname, 'rb')
            f2 = file(tmpfile, 'rb')
            while True:
                x1 = f1.read(4096)
                x2 = f2.read(4096)
                if x1 != x2:
                    break # collision!
                if x1 == '':
                    return # files have been fully examined and they are equal

            # Wow, we actually found a hash collision.  Actually, the key or
            # the existing file probably has the wrong name.  But we will save
            # the file aside just in case, and raise an exception.
            copyfile(tmpfile, '%s-collision' % pathname)
            raise Exception("Hash collision for %s" % key)

        dirname = os.path.dirname(pathname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        copyfile(tmpfile, pathname)

    def __getitem__(self, key):
        pathname = self.__storage_location_else_keyerror(key)
        if not os.access(pathname, os.R_OK):
            raise KeyError(key)
        return iterate_file(pathname)

    def __delitem__(self, key):
        pathname = self.__storage_location_else_keyerror(key)
        if not os.access(pathname, os.R_OK):
            raise KeyError(key)
        os.remove(pathname) # may raise OSError

    def __len__(self):
        # this is obviously O(n) since we have to count everything.
        i = self.iterkeys()
        cnt = 0
        try:
            while True:
                i.next()
                cnt += 1
        except StopIteration:
            return cnt

    def keys(self):
        return list(self.iterkeys())

    def iterkeys(self):
        hash_types = os.walk(self.__storage_directory).next()[1]
        for hash_type in hash_types:
            walker = os.walk(os.path.join(self.__storage_directory, hash_type))
            for dirpath, dirnames, filenames in walker:
                for filename in filenames:
                    possible_urn ='urn:%s:%s' % (hash_type, filename)
                    pathname = os.path.join(dirpath, filename)
                    try:
                        if pathname == self.__storage_location(possible_urn):
                            yield possible_urn
                    except UnsupportedURN:
                        pass

    __iter__ = iterkeys


__b64_chrs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
__contains_only_base64_chrs = sequence_contains_only(__b64_chrs)

def split_urn(urn):
    """Checks to make sure it is a URN we can support

    URN must be in form 'urn:hash_type:hash_value' with base64 characters
    """

    if not isinstance(urn, basestring):
        raise UnsupportedURN(urn)

    urn_split = urn.split(':')
    if len(urn_split) != 3:
        raise UnsupportedURN(urn)

    urn_str, hash_type, digest = urn_split
    if not (urn_str == 'urn'
            and hash_type != ''
            and digest != ''
            and __contains_only_base64_chrs(hash_type)
            and __contains_only_base64_chrs(digest)):
        raise UnsupportedURN(urn)

    return hash_type, digest
