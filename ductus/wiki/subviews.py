# Ductus
# Copyright (C) 2010  Jim Garrison <garrison@wikiotics.org>
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

"""Subviews: a quick way of returning some information based on a resource

This file contains both the subviews framework, as well as some default
subviews for resources.  These subviews can be overriden on a per-type basis by
calling @register_subview(DuctModelName, 'subview-name') within a module's
subviews.py.
"""

from functools import partial

from ductus.wiki import registered_subviews
from ductus.wiki.decorators import register_subview

class Subview(object):
    def __init__(self, resource):
        self._resource = resource

    def __getattr__(self, attr):
        try:
            f = registered_subviews[self._resource.fqn][attr]
        except KeyError:
            f = registered_subviews[None][attr]

        return partial(f, self._resource)

def subview(resource):
    return Subview(resource)

@register_subview(None, 'contributor_set')
def contributor_set(resource):
    """Returns a set of (username, href) tuples.  href can be None."""
    if not hasattr(resource, "common"):
        return set()
    author = resource.common.author
    s = set()
    s.update(*[subview(p.get()).contributor_set()
             for p in resource.common.parents])
    s.add((author.text, author.href or None))
    return s

@register_subview(None, 'subresources')
def subresources(resource):
    """Returns the urns of each resource this resource includes

    (Useful for assembling all the resources necessary for license
    attribution, for instance)
    """
    return set()

@register_subview(None, 'license_info')
def license_info(resource):
    """Returns the resource's license info as an HTML snippet"""
    from django.template import Context, loader
    t = loader.get_template('wiki/license_info.html')
    return t.render(Context({'resource': resource}))
