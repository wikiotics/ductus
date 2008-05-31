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

def iterate_file_object(file_object):
    """This generator function iterates a file-like object, then closes it.
    """

    while True:
        x = file_object.read(4096)
        if x == '':
            file_object.close()
            return
        yield x

def iterate_file(filename):
    """This generator function reads a binary file in chunks.
    """

    with file(filename, 'rb') as f:
        while True:
            x = f.read(4096)
            if x == '':
                return
            yield x

class sequence_contains_only(object):
    """This callable object returns True if a sequence is composed entirely of elements from a given set.

    Initialize the object with a sequence of allowed elements.  When the
    resulting object is called with one argument, it will return True if the
    argument contains only elements from the sequence used during
    initialization.

    Perfect for use with strings!

    >>> f = ductus.util.sequence_contains_only('abcdef')
    >>> f('vegetables')
    False
    >>> f('deadbeef')
    True
    """

    def __init__(self, allowed_elements):
        self.element_list = list(frozenset(allowed_elements))
        self.element_list.sort()
        self.allowed_elements = allowed_elements

    def __call__(self, x):
        x = list(frozenset(x + self.allowed_elements))
        x.sort()
        return (x == self.element_list)