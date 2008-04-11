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

class SafeStorageBackend(object):
    """Wraps a storage backend and removes its delete method."""

    def __init__(self, backend, error_on_delete=False):
        self.__backend = backend
        self.error_on_delete = error_on_delete

    def __contains__(self, key):
        return key in self.__backend

    def __setitem__(self, key, value):
        self.__backend[key] = value

    def __getitem__(self, key):
        return self.__backend[key]

    def __delitem__(self, key):
        if self.error_on_delete:
            raise Exception("Deleting resources is not allowed.")

    def __iter__(self):
        return iter(self.__backend)

    def __len__(self):
        return len(self.__backend)

    def __getattr__(self, attrib):
        return getattr(self.__backend, attrib)
