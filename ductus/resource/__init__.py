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
from ductus.strutil import *

import base64, hashlib
import itertools
import logging
import os
from tempfile import mkstemp

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

class ResourceDatabase(object):
    """
    Main resource database.

    Make sure XML is well-formed.  Verify hashes.

    This module should keep everything consistent as long as the
    backend storage module doesn't mess things up.

    Arguments/attributes:

    * backend storage module to use

    * maximum size allowed for a resource

    * whether to allow XML document types we don't know/support (fixme)
    """

    def __init__(self, storage_backend, max_resource_size=(20*1024*1024)):
        self.storage_backend = storage_backend
        self.max_resource_size = max_resource_size

    def __contains__(self, key):
        return key in self.storage_backend

    @staticmethod
    def is_valid_urn(key):
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

        intended_urn = urn

        header, data_iterator = determine_header(data_iterator)

        # Calculate hash and save to temporary file
        hash_obj = hash_algorithm()
        fd, tmpfile = mkstemp()
        try:
            try:
                data_iterator = self.__check_size(data_iterator)
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
            if urn in self.storage_backend:
                # compare with what we have
                with file(tmpfile, 'rb') as f:
                    for d in self.storage_backend[urn]:
                        dd = f.read(len(d))
                        if dd != d:
                            # Collision!?  Save aside and raise exception
                            self.storage_backend.put_file('%s-collision' % urn,
                                                          tmpfile)
                            raise Exception("hash collision")
                return urn # new resource equals old one

            # If it is an XML file, check it
            if header == 'xml':
                self.__check_xml(urn, tmpfile)

            self.storage_backend.put_file(urn, tmpfile)

        finally:
            os.remove(tmpfile)

        return urn

    def __check_xml(self, urn, filename):
        with file(filename, 'rb') as f:
            f.read(len(bytes('xml\0')))
            tree = etree.parse(f)

        # Make sure we recognize the root node and the document is valid
        # wrt DTD or relaxng (fixme)

        # Find all urn:hash_type:hash_value links and ensure they are not broken
        links = set()
        for event, element in etree.iterwalk(tree):
            if '{http://www.w3.org/1999/xlink}href' in element.attrib:
                links.add(element.attrib['{http://www.w3.org/1999/xlink}href'])
        for link in links:
            if link.startswith('urn:%s:' % hash_name) and link not in self:
                raise Exception("Broken link from %s to %s"
                                % (urn, link))

    def __check_size(self, data_iterator):
        cumulative_size = 0
        while True:
            data = data_iterator.next()
            cumulative_size += len(data)
            if cumulative_size > self.max_resource_size:
                raise SizeTooLargeError("Resource is greater than limit of %d bytes." % self.max_resource_size)
            yield data

    def store_blob(self, x, urn=None):
        return self.store(itertools.chain((bytes("blob\0"),), x), urn)

    def store_xml(self, x, urn=None):
        return self.store(itertools.chain((bytes("xml\0"),), x), urn)

    def get_blob(self, urn):
        header, data_iterator = determine_header(self[urn], False)
        if header != 'blob':
            raise Exception()
        return data_iterator

    def get_xml(self, urn):
        header, data_iterator = determine_header(self[urn], False)
        if header != 'xml':
            raise Exception()
        return data_iterator

    def get_xml_tree(self, urn):
        from StringIO import StringIO
        # following line could be simplified if the data_iterator had
        # a "read" method instead ...
        return etree.parse(StringIO(''.join(self.get_xml(urn))))

    def keys(self):
        "This will be easy... just query the database."

    def __getitem__(self, key):
        return self.storage_backend[key]

def determine_header(data_iterator, replace_header=True):
    buf = bytes()

    try:
        while (bytes("\0") not in buf and len(buf) < 256):
            buf += data_iterator.next()
    except StopIteration:
        data_iterator = iter(())

    try:
        header = buf[:buf.index("\0")]
    except ValueError:
        raise InvalidHeader("Invalid resource: No header or header too long")
    if header not in ('xml', 'blob'):
        raise InvalidHeader("Invalid or unknown header")

    if not replace_header:
        buf = buf[buf.index("\0")+1:]
    data_iterator = itertools.chain((buf,), data_iterator)

    return unicode(header), data_iterator
