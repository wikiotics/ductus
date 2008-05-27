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
    element.attrib[ns('xlink', 'type')] = 'simple'
    element.attrib[ns('xlink', 'href')] = uri

def make_ns_func(nsmap):
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
