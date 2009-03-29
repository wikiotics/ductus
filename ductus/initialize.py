# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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

from django.conf import settings
from django.utils.importlib import import_module

from ductus.resource import ResourceDatabase
from ductus.util import ignore

def create_resource_database():
    """Initialize ResourceDatabase using DUCTUS_STORAGE_BACKEND"""
    backend = settings.DUCTUS_STORAGE_BACKEND
    mod_name, junk, var_name = backend.rpartition('.')
    storage_backend = getattr(import_module(mod_name), var_name)
    ResourceDatabase(storage_backend)

def register_installed_modules():
    """Register each module in DUCTUS_INSTALLED_MODULES"""
    for module in getattr(settings, "DUCTUS_INSTALLED_MODULES", ()):
        import_module('.views', module)
        for submod in ('edit_views', 'models'):
            with ignore(ImportError):
                import_module('.' + submod, module)

create_resource_database()
register_installed_modules()
