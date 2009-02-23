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

class WrapStorageBackend(object):
    """Wraps a storage backend, maintaining its full functionality."""

    def __init__(self, backend):
        self.__backend = backend

    def __contains__(self, key):
        return key in self.__backend

    def put_file(self, key, tmpfile):
        self.__backend.put_file(key, tmpfile)

    def __getitem__(self, key):
        return self.__backend[key]

    def __delitem__(self, key):
        del self.__backend[key]

    def __iter__(self):
        return iter(self.__backend)

    def __len__(self):
        return len(self.__backend)

    def __getattr__(self, attrib):
        return getattr(self.__backend, attrib)
