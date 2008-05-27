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

def add_simple_xlink(element, uri):
    """Makes the XML element into an xlink that points to the given URI.

    >>> from lxml import etree
    >>> elt = etree.Element("root")
    >>> add_simple_xlink(elt, "http://example.com/")
    >>> etree.tostring(elt)
    '<root xmlns:ns0="http://www.w3.org/1999/xlink" ns0:type="simple" ns0:href="http://example.com/"/>'

    """

    element.attrib['{http://www.w3.org/1999/xlink}type'] = 'simple'
    element.attrib['{http://www.w3.org/1999/xlink}href'] = uri

def make_ns_func(nsmap):
    """Creates a convenience function for dealing with XML namespaces.

    >>> nsmap = { 
    ...     None: 'http://wikiotics.org/ns/2008/picture',
    ...     'xlink': 'http://www.w3.org/1999/xlink',
    ... }
    >>> ns = make_ns_func(nsmap)
    >>> ns('root')
    '{http://wikiotics.org/ns/2008/picture}root'
    >>> ns('xlink', 'href')
    '{http://www.w3.org/1999/xlink}href'

    """

    def ns_func(*args):
        n = len(args)
        if n == 1:
            x = (nsmap[None], args[0])
        elif n == 2:
            x = (nsmap[args[0]], args[1])
        else:
            raise TypeError("ns_func expecting 1 or 2 arguments, got %d" % n)
        return '{%s}%s' % x
    return ns_func
