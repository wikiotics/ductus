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

from contextlib import contextmanager
from tempfile import mkstemp
import os

from django.utils import six

BLOCK_SIZE = 8192

def iterate_file_object(file_object):
    """This generator function iterates a file-like object, then closes it.
    """

    try:
        while True:
            x = file_object.read(BLOCK_SIZE)
            if x == '':
                return
            yield x
    finally:
        file_object.close()

def iterate_file(filename):
    """This generator function reads a binary file in chunks.
    """

    with file(filename, 'rb') as f:
        while True:
            x = f.read(BLOCK_SIZE)
            if x == '':
                return
            yield x

def _default_delete_func(filename):
    with ignore(OSError):
        os.remove(filename)

def iterate_file_then_delete(filename, delete_func=_default_delete_func):
    """Reads a binary file in chunks and then deletes it.

    Delete occurs when the iterator is garbage-collected or if an exception
    occurs while reading the file.
    """

    def gen():
        try:
            data_iterator = iterate_file(filename)
            yield # see comment below
            while True:
                data = six.next(data_iterator)
                yield data
        finally:
            del data_iterator
            delete_func(filename)

    retval = gen()

    # Execute the generator until the first yield statement.
    # This elaborate scheme is necessary so the "finally" block
    # is always executed, even if the iterator is
    # garbage-collected before it is used.
    six.next(retval)

    return retval

def iterator_to_tempfile(data_iterator, **kwargs):
    """Saves an iterator to a new temporary file.

    Returns: the name of the file
    """
    fd, tmpfile = mkstemp(**kwargs)
    f = os.fdopen(fd, 'wb')
    try:
        try:
            for data in data_iterator:
                f.write(data)
        finally:
            f.close()
    except:
        with ignore(OSError):
            os.remove(tmpfile)
        raise
    return tmpfile

class sequence_contains_only(object):
    """This callable object returns True if a sequence is composed entirely of elements from a given set.

    Initialize the object with a sequence of allowed elements.  When the
    resulting object is called with one argument, it will return True if the
    argument contains only elements from the sequence used during
    initialization.

    Perfect for use with strings!

    >>> f = sequence_contains_only('abcdef')
    >>> f('vegetables')
    False
    >>> f('deadbeef')
    True
    """

    def __init__(self, allowed_elements):
        self.element_list = frozenset(allowed_elements)
        self.allowed_elements = allowed_elements

    def __call__(self, x):
        return self.element_list == frozenset(x + self.allowed_elements)

def remove_adjacent_duplicates(list_):
    """Removes adjacent duplicates from a list.

    Operates on the list in place.  If the list happens to be sorted,
    all duplicates will be removed.
    """

    last = list_[-1]
    for i in range(len(list_) - 2, -1, -1):
        if last == list_[i]:
            del list_[i]
        else:
            last = list_[i]

@contextmanager
def ignore(*exceptions):
    """Ignore given exceptions in a block of code

    with ignore(OSError):
        import os
        os.remove('/tmp/ductus_foo')
    """

    try:
        yield
    except exceptions:
        pass
    except:
        if exceptions != ():
            raise

def create_property(f):
    """Helper decorator for creating properties

    >>> class A(object):
    ...     @create_property
    ...     def monty():
    ...         def fget(s):
    ...             return 43
    ...         return locals()
    ...
    >>> A().monty
    43

    """
    return property(**f())

def is_punctuation(v):
    """Returns true if the given character is a punctuation mark"""
    assert len(v) == 1
    import unicodedata
    return unicodedata.category(unicode(v)).startswith("P")
