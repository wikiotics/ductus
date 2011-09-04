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

from gridfs import GridFS, NoFile

from ductus.util import iterate_file_object

class GridfsStorageBackend(object):
    def __init__(self, db, collection_name="storage"):
        self.fs = GridFS(db, collection_name)

    def __get_file_object(self, key):
        try:
            return self.fs.get_version(filename=key)
        except NoFile:
            raise KeyError(key)

    def __contains__(self, key):
        return self.fs.exists(filename=key)

    def __getitem__(self, key):
        return iterate_file_object(self.__get_file_object(key))

    def put_file(self, key, tmpfile):
        with file(tmpfile) as f:
            self.fs.put(f, filename=key)

    def __delitem__(self, key):
        self.fs.delete(self.__get_file_object(key)._id)

    def keys(self):
        return self.fs.list()

    iterkeys = keys

    __iter__ = iterkeys

    def __len__(self):
        return len(self.keys())
