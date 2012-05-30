# Ductus
# Copyright (C) 2012  Jim Garrison <garrison@wikiotics.org>
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

from django.conf import settings
from django.utils.importlib import import_module

_indexing_mongo_database = False  # False means uninitialized; None means
                                  # indexing is not in use

def get_indexing_mongo_database():
    """Returns the pymongo database object used for indexing"""
    global _indexing_mongo_database
    if _indexing_mongo_database == False:
        indexing_db_obj = getattr(settings, "DUCTUS_INDEXING_MONGO_DATABASE", None)
        if indexing_db_obj is None:
            _indexing_mongo_database = None
        else:
            mod_name, junk, var_name = indexing_db_obj.rpartition('.')
            _indexing_mongo_database = getattr(import_module(mod_name), var_name)
    return _indexing_mongo_database
