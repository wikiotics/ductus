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

from ductus.wiki import registered_views

def register_view(root_tag_name, *args):
    """Registers a URN view function.

    root_tag_name should include the namespace information.  Additional
    arguments specify which views are defined.  The default view is specified
    by passing 'None' as an argument.
    """

    if len(args) == 0:
        raise TypeError("function requires at least two arguments")
    def _register_view(func):
        for arg in args:
            registered_views.setdefault(root_tag_name, dict())[arg] = func
        return func
    return _register_view

def unvarying(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        response._unvarying = True
        return response
    return new_func
