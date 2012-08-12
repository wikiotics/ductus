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
from ductus.wiki.namespaces import registered_namespaces, split_pagename

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

class IndexingError(Exception):
    """a basic Exception for index related errors"""
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value

def search_pages(tags):
    """
    return a list of pages tagged with all `tags` (boolean AND)
    like [{"absolute_pagename": name, "path": path}]

    :param tags: a list of tag values like: ['tag1', 'target-language:en']. This is assumed to be valid tags, no checking is performed in this function!
    """

    if not tags:
        # fixme: we should prompt the user for what they want to search
        raise IndexingError('your search query cannot be empty')

    #from ductus.index import get_indexing_mongo_database
    indexing_db = get_indexing_mongo_database()
    if indexing_db is None:
        raise IndexingError("indexing database is not available")
    collection = indexing_db.urn_index

    # construct the mongodb query
    query = {}
    query["tags"] = {"$all": tags}

    # perform the search
    query["current_wikipages"] = {"$not": {"$size": 0}}
    pages = collection.find(query, {"current_wikipages": 1}).sort("current_wikipages")
    results = []
    for page in pages:
        absolute_pagename = page["current_wikipages"][0]
        prefix, pagename = split_pagename(absolute_pagename)
        try:
            wns = registered_namespaces[prefix]
        except KeyError:
            # for some reason there's a prefix we don't know about.  move
            # along.
            pass
        else:
            path = "/%s/%s" % (prefix, wns.path_func(pagename))
            results.append({
                "absolute_pagename": absolute_pagename,
                "path": path,
            })

    return results
