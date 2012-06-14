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

import logging

from django.core.management.base import NoArgsCommand
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(NoArgsCommand):
    help = "maintain the ductus wikipage/urn index"

    def handle_noargs(self, **options):
        from ductus.index import get_indexing_mongo_database
        indexing_db = get_indexing_mongo_database()
        if indexing_db is None:
            raise Exception
        collection = indexing_db.urn_index

        def perform_upsert(urn, obj, ignore=None):
            # REMEMBER that dictionary order matters in mongodb; we just ignore
            # it

            # fixme: first inspect element to see if things might already be
            # right.  also check to make sure there aren't any unexpected
            # attributes on the toplevel element.  and do the same thing for
            # blobs too.

            obj = dict(obj)
            obj["urn"] = urn
            collection.update({"urn": urn}, obj, upsert=True, safe=True)
            verified_urns.add(urn)

        logging.basicConfig(level=logging.INFO) # FIXME

        # create the mongodb indexes
        collection.ensure_index("urn", unique=True, drop_dups=True)
        collection.ensure_index("parents", sparse=True)
        collection.ensure_index("tags", sparse=True)
        collection.ensure_index("links")
        collection.ensure_index("recursive_links")

        # Begin actual code

        from lxml import etree

        from ductus.resource import get_resource_database, UnexpectedHeader, hash_name
        from ductus.wiki.models import WikiPage

        resource_database = get_resource_database()

        verified_urns = set()
        current_wikipages_map = {}

        operations = {None: 0}

        def verify(urn):
            """Updates a urn's indexing info and returns the set of its recursive links
            """
            operations[None] += 1
            logger.info("operation %d: processing %s", operations[None], urn)

            if urn in verified_urns:
                q = collection.find_one({"urn": urn}, {"recursive_links": 1})
                try:
                    return set(q["recursive_links"])
                except KeyError:
                    return set()

            try:
                tree = resource_database.get_xml_tree(urn)
            except UnexpectedHeader:
                # it must be a blob
                perform_upsert(urn, {"fqn": None})
                return set()

            links = set()
            for event, element in etree.iterwalk(tree):
                if '{http://www.w3.org/1999/xlink}href' in element.attrib and element.getparent().tag != '{http://ductus.us/ns/2009/ductus}parents':
                    link = element.attrib['{http://www.w3.org/1999/xlink}href']
                    if link.startswith('urn:%s:' % hash_name):
                        links.add(link)

            recursive_links = set(links)
            for link in links:
                additional_links = verify(link)
                recursive_links.update(additional_links)

            resource = resource_database.get_resource_object(urn)

            assert resource.fqn is not None
            obj = {
                "fqn": resource.fqn,
                "links": list(links),
                "recursive_links": sorted(recursive_links),
                "current_wikipages": sorted(current_wikipages_map.get(urn, ())),
            }
            try:
                obj["parents"] = sorted([parent.href for parent in resource.common.parents])
                obj["tags"] = sorted([tag.value for tag in resource.tags])
            except AttributeError:
                pass
            perform_upsert(urn, obj)

            return recursive_links

        for wikipage in WikiPage.objects.all():
            revision = wikipage.get_latest_revision()
            if revision is not None and revision.urn:
                urn = 'urn:' + revision.urn
                current_wikipages_map.setdefault(urn, set()).add(wikipage.name)

        n_attempted = n_successful = 0
        for key in resource_database.iterkeys():
            n_attempted += 1
            try:
                verify(key)
            except Exception:
                logger.warning("Key failed: %s", key)
            else:
                n_successful += 1

        logger.info("Successfully processed %d of %d keys", n_successful, n_attempted)
