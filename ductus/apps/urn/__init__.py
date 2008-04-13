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

def get_resource_database():
    global __resource_database
    if __resource_database is None:
        from django.conf import settings
        backend = settings.DUCTUS_STORAGE_BACKEND
        mod_name, junk, var_name = backend.rpartition('.')
        storage_backend = getattr(__import__(mod_name, {}, {}, ['']),
                                      var_name)
        from ductus.resource import ResourceDatabase
        __resource_database = ResourceDatabase(storage_backend)
    return __resource_database

__resource_database = None
