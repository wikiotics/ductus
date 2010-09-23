#!/usr/bin/env python

from lxml import etree

import ductus.initialize
from ductus.resource import get_resource_database, UnexpectedHeader
from ductus.wiki.models import WikiRevision

# This script loads everything into memory, which works for our purposes but
# wouldn't if there were a higher number of objects in the database

HREF_FQN = '{http://www.w3.org/1999/xlink}href'
DEFAULT_LICENSE = 'http://creativecommons.org/licenses/by-sa/3.0/'

rdb = get_resource_database()

urn_update_map = {}

def update_object(urn, default_author):
    if urn in urn_update_map:
        return urn_update_map[urn]
    new_urn = _update_object(urn, default_author)
    urn_update_map[urn] = new_urn
    print new_urn
    return new_urn

def _update_object(urn, default_author):
    try:
        tree = rdb.get_xml_tree(urn)
    except UnexpectedHeader:
        # must be a blob
        return urn
    for event, element in etree.iterwalk(tree):
        if HREF_FQN in element.attrib:
            link = element.attrib[HREF_FQN]
            if link.startswith('urn:'):
                element.attrib[HREF_FQN] = update_object(link, default_author)
    do_actual_update(tree, default_author)
    root = tree.getroot()
    return rdb.store_xml_tree(root)

def do_actual_update(tree, default_author):
    root = tree.getroot()
    for child in root:
        if child.tag == '{http://ductus.us/ns/2009/ductus}common':
            log_message_index = parents_index = licenses_index = -1
            for i, grandchild in enumerate(child):
                if grandchild.tag == '{http://ductus.us/ns/2009/ductus}author':
                    if not grandchild.text:
                        grandchild.text = default_author
                elif grandchild.tag == '{http://ductus.us/ns/2009/ductus}licenses':
                    licenses_index = i
                    licenses_elt = grandchild
                elif grandchild.tag == '{http://ductus.us/ns/2009/ductus}parents':
                    parents_index = i
                elif grandchild.tag == '{http://ductus.us/ns/2009/ductus}log_message':
                    log_message_index = i
            if licenses_index == -1:
                licenses_elt = etree.Element('{http://ductus.us/ns/2009/ductus}licenses')
                child.insert(log_message_index, licenses_elt)
            # find it; add cc-by-sa if nonempty
            if len(licenses_elt) == 0:
                license_elt = etree.SubElement(licenses_elt, '{http://ductus.us/ns/2009/ductus}item')
                license_elt.set('{http://www.w3.org/1999/xlink}type', 'simple')
                license_elt.set('{http://www.w3.org/1999/xlink}href', DEFAULT_LICENSE)

# We will start with every urn referenced explicitly by a WikiRevision.  We
# will deal with them in chronological order so we set the author based on the
# earliest reference to the urn.
for rev in WikiRevision.objects.order_by('timestamp').all():
    if not rev.urn:
        continue
    author = (rev.author and rev.author.username) or rev.author_ip
    urn = 'urn:%s' % rev.urn
    urn = update_object(urn, author)
    rev.urn = urn[4:]
    rev.save()
