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
from ductus.resource import get_resource_database, hash_name, UnexpectedHeader
from ductus.wiki.namespaces import registered_namespaces, split_pagename
from lxml import etree

_indexing_mongo_database = False  # False means uninitialized; None means
                                  # indexing is not in use

def get_indexing_mongo_database():
    """Returns the pymongo database object used for indexing"""
    global _indexing_mongo_database
    if _indexing_mongo_database is False:
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

def search_pages(**kwargs):
    """
    return a list of pages tagged with all `tags` (boolean AND)
    like [{"absolute_pagename": name, "path": path}]

    :param **kwargs: the search parameters (which are $and'ed together, so a page must match all criteria to be returned). Format:
        {
        tags: a list of tag values like: ['tag1', 'target-language:en']. This is assumed to be valid tags, no checking is performed in this function!
        pagename: a string to (partially) match in the page urls/names
        notags: a special argument that searches for pages with no tags.
        }
    """

    if not len(kwargs):
        # fixme: we should prompt the user for what they want to search
        raise IndexingError('your search query cannot be empty')

    indexing_db = get_indexing_mongo_database()
    if indexing_db is None:
        raise IndexingError("indexing database is not available")
    collection = indexing_db.urn_index

    # construct the mongodb query
    query = {}
    query["current_wikipages"] = {"$not": {"$size": 0}}
    for key in kwargs:
        if key == 'tags' and kwargs[key]:
            query["tags"] = {"$all": kwargs[key]}
        if key == 'pagename':
            query['current_wikipages']['$regex'] = kwargs[key]
            query['current_wikipages']['$options'] = 'i'
        if key == 'notags':
            # special search feature to report all pages without tags
            query["tags"] = {"$size": 0}
            break

    if len(query) > 1:
        query = {'$and': [query]}

    # perform the search
    pages = collection.find(query, {"current_wikipages": 1, "tags": 1}).sort("current_wikipages")
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
                "tags": page["tags"],
            })

    return results

def get_list_of_target_lang_codes():
    """return the list of all language codes used as target-language tags in lessons"""
    indexing_db = get_indexing_mongo_database()
    if indexing_db is None:
        raise IndexingError("indexing database is not available")
    collection = indexing_db.urn_index

    tags = filter(lambda tag: tag is not None and tag.startswith('target-language:'), collection.distinct('tags'))
    return [tag.split(':')[1] for tag in tags]

def perform_upsert(collection, urn, obj, ignore=None):
    """Update/insert the index document for a `urn` in mongo.

    `collection` is the collection for the index.
    `urn`: the urn for which to store the object.
    `obj`: a dict object representing the data to store.
    """
    # REMEMBER that dictionary order matters in mongodb; we just ignore
    # it

    # fixme: first inspect element to see if things might already be
    # right.  also check to make sure there aren't any unexpected
    # attributes on the toplevel element.  and do the same thing for
    # blobs too.

    obj = dict(obj)
    obj["urn"] = urn
    collection.update({"urn": urn}, obj, upsert=True, safe=True)

def verify(collection, urn, current_wikipages_list, force_update=False):
    """Updates a urn's indexing info and returns the set of its recursive links.

    `collection`: the mongo collection to use as returned by ``get_indexing_mongo_database()``.
    `urn`: the urn to update the index for, starting with "urn:".
    `wikipages_url_list` is the sorted list of urls pointing to `urn`.
    `force_update`: set to True to update the index even if `urn` is already in the index (defaults to ``False``).
    """
    if not force_update:
        q = collection.find_one({"urn": urn}, {"recursive_links": 1})
        if q:
            try:
                return set(q["recursive_links"])
            except KeyError:
                return set()

    resource_database = get_resource_database()

    try:
        tree = resource_database.get_xml_tree(urn)
    except UnexpectedHeader:
        # it must be a blob
        perform_upsert(collection, urn, {"fqn": None})
        return set()

    links = set()
    for event, element in etree.iterwalk(tree):
        if '{http://www.w3.org/1999/xlink}href' in element.attrib and element.getparent().tag != '{http://ductus.us/ns/2009/ductus}parents':
            link = element.attrib['{http://www.w3.org/1999/xlink}href']
            if link.startswith('urn:%s:' % hash_name):
                links.add(link)

    recursive_links = set(links)
    for link in links:
        additional_links = verify(collection, link, [])
        recursive_links.update(additional_links)

    resource = resource_database.get_resource_object(urn)

    assert resource.fqn is not None
    obj = {
        "fqn": resource.fqn,
        "links": list(links),
        "recursive_links": sorted(recursive_links),
        "current_wikipages": sorted(current_wikipages_list),
    }
    try:
        obj["parents"] = sorted([parent.href for parent in resource.common.parents])
        obj["tags"] = sorted([tag.value for tag in resource.tags])
    except AttributeError:
        pass
    perform_upsert(collection, urn, obj)

    return recursive_links


def update_index_on_save(urn, url, parent_urn=None):
    """
    Update the index for the specified urn (to be used when saving a blueprint), and for its parents (if any, i.e: if modifying an existing wikipage).
    Note that this function assumes a single url is linked to the urn, which is true only for wiki edits. Do not call this function for maintenance purposes.

    `urn` is the urn of the newly saved blueprint (ie: the latest revision). Must start with 'urn:'.
    `url` is an array of urls under which the urn is saved. Empty array means delete the page ("unlink" it, the urn remains in the index).
    `parent_urn` is the urn to the parent of `urn` (optional).
    """
    indexing_db = get_indexing_mongo_database()
    if indexing_db is None:
        raise Exception
    collection = indexing_db.urn_index

    verify(collection, urn, url, force_update=(url==[]))
    if parent_urn:
        verify(collection, parent_urn, [], force_update=True)
