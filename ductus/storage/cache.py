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

import os, tempfile
import ductus.util

class CacheStorageBackend(object):
    """
    Caches a backend using another one as cache.

    Currently there is no limit to the cache size and nothing will be
    deleted from it automatically.
    """

    def __init__(self, backing_store, cache):
        self.__backing_store = backing_store
        self.__cache = cache

    def __attempt_cache_save(self, key, value):
        try:
            self.__cache[key] = value
            return True
        except Exception:
            return False

    def __contains__(self, key):
        return key in self.__cache or key in self.__backing_store

    def __setitem__(self, key, value):
        self.__backing_store[key] = value
        self.__attempt_cache_save(key, value)

    def __getitem__(self, key):
        try:
            return self.__cache[key]
        except Exception:
            data_iterator = self.__backing_store[key]

            # Cache it
            fd, tmpfile = tempfile.mkstemp()
            try:
                for data in data_iterator:
                    os.write(fd, data)
            finally:
                os.close(fd)
            self.__attempt_cache_save(key, tmpfile)

            return ductus.util.iterate_file(tmpfile)

    def __delitem__(self, key):
        del self.__backing_store[key]
        try:
            del self.__cache[key]
        except KeyError:
            from logging import warning
            warning("Error while removing %s from cache." % key)

    def keys(self):
        # Assume all items in cache are in backing_store
        return self.__backing_store.keys()

    def iterkeys(self):
        # Assume all items in cache are in backing_store
        return iter(self.__backing_store)

    __iter__ = iterkeys

    def __len__(self):
        # Assume all items in cache are in backing_store
        return len(self.__backing_store)
