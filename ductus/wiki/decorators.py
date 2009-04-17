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

from ductus.wiki import registered_views, registered_creation_views

def register_view(model, label=None, requires=(lambda d: d.resource)):
    """Registers a URN view function.
    """

    fqn = None if model is None else model.fqn
    if requires is None:
        requires = lambda d: True # accept everything; no requirements
    def _register_view(func):
        func.meets_requirements = requires # boolean function
        registered_views.setdefault(fqn, dict())[label] = func
        return func
    return _register_view

def register_creation_view(model):
    def _register_creation_view(func):
        if model.root_name in registered_creation_views:
            raise Exception("A model is already registered with this root_name: %s"
                            % registered_creation_views[model.root_name])
        registered_creation_views[model.root_name] = func
        return func
    return _register_creation_view

def unvarying(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        response._unvarying = True
        return response
    return new_func
