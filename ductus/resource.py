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

from __future__ import with_statement

import base64, hashlib
import itertools
import logging
import os
from tempfile import mkstemp

import elixir, sqlalchemy
from lxml import etree

hash_name = "sha384"
hash_encode = base64.urlsafe_b64encode
hash_decode = base64.urlsafe_b64decode
hash_algorithm = getattr(hashlib, hash_name)
hash_digest_size = hash_algorithm().digest_size

max_urn_length = len('urn:%s:%s' % (hash_name,
                                    hash_encode(hash_algorithm('').digest())))

class InvalidHeader(ValueError):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

class SizeTooLargeError(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

# store public or system DTD in database?  or both?  need a policy decision here

# we could just store public DTD's and only allow them... and have a
# database of what they are supposed to mean sitting around locally.

class DtdInfo(elixir.Entity):
    dtd = elixir.Field(elixir.String, required=True, unique=True)

class ResourceInfo(elixir.Entity):
    urn = elixir.Field(elixir.String(75), required=True, unique=True)
    dtd = elixir.ManyToOne('DtdInfo') # None <=> blob
    links = elixir.ManyToMany('ResourceInfo')

def __check_xml_and_prepare_update(urn, filename):
    ""
    # option: allow import of files with DTDs we don't recognize?

    # Parse file and determine DTD
    tree = etree.parse(filename)
    dtd = tree.docinfo.system_url, tree.docinfo.public_id

    # validate DTD and find all URN links
    links = set()
    for event, element in etree.iterwalk(tree, dtd_validation=True):
        if '{http://www.w3.org/1999/xlink}href' in element.attrib:
            links.add(element.attrib['{http://www.w3.org/1999/xlink}href'])
    links = [x for x in links if x[:4] == 'urn:']

    # get primary key of each link destination; raise exception if
    # one is unknown/broken
    q = ResourceInfo.query.filter(sqlalchemy.or_(*[ResourceInfo.urn == u
                                                   for u in links]))
    link_destinations = list(q)
    if len(link_destinations) != len(links):
        # fixme: say which one is broken
        raise Exception("Broken link in XML document")

    # prepare update function/transaction
    def update_database_for_xml():
        ri = ResourceInfo(urn=urn, dtd=dtdi, links=link_destinations)
        elixir.session.flush()
    return update_database_for_xml

def __check_blob_and_prepare_update(urn, filename):
    def update_database_for_blob():
        ri = ResourceInfo(urn=urn)
        elixir.session.flush()
    return update_database_for_blob

__check_and_prepare_update = {
    'xml': __check_xml_and_prepare_update,
    'blob': __check_blob_and_prepare_update,
}

class ResourceDatabase(object):
    """
    Main resource database.

    Keep track of what resources reference each other.  Make sure XML
    is well-formed.  Verify hashes.

    This module should keep everything consistent as long as the
    backend storage module doesn't mess things up.

    Arguments/attributes:

    * backend storage module to use.

    * whether to allow documents with DTDs we don't know/support
    """

    def __init__(self, storage_backend):
        self.storage_backend = storage_backend

    def __contains__(self, key):
        return ResourceInfo.query.filter_by(urn=key).one() is not None

    @staticmethod
    def supported_key(key):
        if isinstance(key, str):
            urn_str, hash_type, digest = key.split(':')
            if urn_str == 'urn' and hash_type == hash_name:
                try:
                    decoded = hash_decode(digest)
                    if len(decoded) == hash_digest_size:
                        return True
                except TypeError:
                    return False
        return False

    def store(self, data_iterator, urn=None):
        """x is an iterator that returns all data.

        Returns the urn or could raise some exceptions."""

        # Issue a warning if data_iterator is a string in disguise.  Such a
        # condition is relatively harmless, but it would slow things down since
        # hash.update() would be called once for each byte.
        if isinstance(data_iterator, str):
            logging.warning("String passed as data_iterator.")

        intended_urn = urn

        # Determine header
        header, data_iterator = determine_header(data_iterator)

        # Calculate hash and save to temporary file
        hash_obj = hash_algorithm()
        fd, tmpfile = mkstemp()
        try:
            try:
                data_iterator = __check_size(data_iterator)
                for data in data_iterator:
                    hash_obj.update(data)
                    os.write(fd, data)
            finally:
                os.close(fd)

            digest = hash_encode(hash_obj.digest())
            urn = "urn:%s:%s" % (hash_name, digest)
            if intended_urn and intended_urn != urn:
                raise "URN given does not match content." # valueerror

            # Do we already have this urn in the DB?
            existing_entry = ResourceInfo.query.filter_by(urn=urn).one()
            if existing_entry:
                # compare with what we have
                with file(tmpfile, 'rb') as f:
                    for d in self.storage_backend[urn]:
                        dd = f.read(len(d))
                        if dd != d:
                            # Collision!?  Save aside and raise exception
                            self.storage_backend[urn + '-collision'] = tmpfile
                return urn # new resource equals old one

            db_update_func = __check_and_prepare_update[header](urn, tmpfile)
            self.storage_backend[urn] = tmpfile

        finally:
            os.remove(tmpfile)

        db_update_func() # Maybe this raises an exception if the row
                         # already exists in the database?  We should
                         # handle this...

        return urn

    def store_blob(self, x, urn=None):
        return self.store(itertools.chain(("blob\0",), x), urn)

    def store_xml(self, x, urn=None):
        return self.store(itertools.chain(("xml\0",), x), urn)

    def keys(self):
        "This will be easy... just query the database."

    def __getitem__(self, key):
        # fixme: query database to make sure it is known (if not raise KeyError)
        return self.storage_backend[key]

    def __setitem__(self, key, value):
        self.store(value, key)

def determine_header(data_iterator, replace_header=True):
    buf = str() # explicitly not unicode

    try:
        while ("\0" not in buf and len(buf) < 256):
            buf += data_iterator.next()
    except StopIteration:
        data_iterator = []

    try:
        header = buf[:buf.index("\0")]
    except ValueError:
        raise InvalidHeader("Invalid resource: No header or header too long")
    if header not in __check.keys():
        raise InvalidHeader("Invalid or unknown header")

    if not replace_header:
        buf = buf[buf.index("\0")+1:]
    data_iterator = itertools.chain((buf,), data_iterator) # replace header
        
    return header, data_iterator

def __check_size(data_iterator):
    cumulative_size = 0
    while True:
        data = data_iterator.next()
        cumulative_size += len(data)
        if cumulative_size > MAX_RESOURCE_SIZE:
            raise SizeTooLargeError("Resource is greater than MAX_RESOURCE_SIZE (%d bytes)." % MAX_RESOURCE_SIZE)
        yield data
