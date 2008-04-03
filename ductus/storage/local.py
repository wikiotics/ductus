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

import ductus.util, ductus.urn

class LocalStorageBackend(object):
    """Local storage backend.

    This backend supports only Class-A URN's (as defined in ductus.urn).
    """

    def __init__(self, storage_directory):
        self.__storage_directory = storage_directory

    def __storage_location(self, urn):
        ductus.urn.verify_class_A_urn(urn)
        urn_str, hash_type, digest = urn.split(':')
        path = filter(lambda x: x, (self.__storage_directory, hash_type,
                                    digest[0:2], digest[2:4], digest))
        return os.path.join(*path)

    def __contains__(self, key):
        # does file exist, and can we read it?
        return os.access(self.__storage_location(key), os.R_OK)

    def __setitem__(self, key, tmpfile):
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

            # Wow, we actually found a hash collision.  Save the file aside and
            # raise an exception.
            copyfile(tmpfile, self.__storage_location('%s-collision' % key))
            raise Exception("Hash collision for %s" % key)

        dirname = os.path.dirname(pathname)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        copyfile(tmpfile, pathname)

    def __getitem__(self, key):
        pathname = self.__storage_location(key)
        if not os.access(pathname, os.R_OK):
            raise KeyError
        return ductus.util.iterate_file(pathname)

    def __delitem__(self, key):
        pathname = self.__storage_location(key)
        if not os.access(pathname, os.R_OK):
            raise KeyError
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
                    except ductus.urn.UnsupportedURN:
                        pass
