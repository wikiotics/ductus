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

    Call constructor with a sequence of allowed elements.  When the resulting
    object is called with one argument, it will return True if the argument
    contains only elements from that sequence used during initialization.

    Perfect for use with strings!

    >>> f = ductus.util.sequence_contains_only('abcdef')
    >>> f('vegetables')
    False
    >>> f('deadbeef')
    True
    """

    def __init__(self, allowed_characters):
        self.character_list = list(frozenset(allowed_characters))
        self.character_list.sort()
        self.allowed_characters = allowed_characters

    def __call__(self, x):
        x = list(frozenset(x + self.allowed_characters))
        x.sort()
        return (x == self.character_list)
