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

class UnionStorageBackend(object):
    """
    Union of two or more resource libraries.

    Initialized with multiple backends as arguments.  New resources are always
    saved in the first backend (even if that resource already exists in
    another).  Fetching of resources searches each backend in order.  Delete
    does nothing currently.

    """

    def __init__(self, *backends):
        assert len(backends) > 0
        self.__backends = backends

    def __contains__(self, key):
        for backend in self.__backends:
            if key in backend:
                return True
        return False

    def put_file(self, key, filename):
        primary_backend = self.__backends[0]
        primary_backend.put_file(key, filename)

    def __getitem__(self, key):
        for backend in self.__backends:
            try:
                return backend[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __delitem__(self, key):
        pass

    def keys(self):
        # Sadly, this seems like the only way to do it.
        all_keys = set()
        for backend in self.__backends:
            all_keys.update(backend)
        return list(all_keys)

    def iterkeys(self):
        return iter(self.keys())

    __iter__ = iterkeys

    def __len__(self):
        # Horrible, horrible!
        return len(self.keys())
