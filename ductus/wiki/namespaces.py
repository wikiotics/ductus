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

from django.conf import settings

registered_namespaces = {}

class BaseWikiNamespace(object):
    allow_page_creation = False

    def __init__(self, prefix):
        self.prefix = prefix
        # register ourselves
        assert prefix not in registered_namespaces
        registered_namespaces[prefix] = self

    def page_exists(self, pagename):
        """Does the given page exist?

        Used to mark whether a link is broken
        """
        raise NotImplementedError

    def allow_edit(self, user, pagename):
        """Does the user have permission to edit the page?"""
        return False

    def view_page(self, request, pagename):
        """the Django view for the resource"""
        raise NotImplementedError

    def path_func(self, pagename):
        """Format pagename for inclusion in a url"""
        from django.utils.encoding import iri_to_uri
        from django.utils.http import urlquote
        return iri_to_uri(urlquote(pagename))

class WikiPrefixNotProvided(Exception):
    pass

def split_pagename(absolute_pagename, fallback_prefix=None):
    before_slash = absolute_pagename.split('/', 1)[0]
    if ':' in before_slash:
        # we were indeed given an absolute pagename.  split it and return
        return tuple(absolute_pagename.split(':', 1))

    # we weren't actually given an absolute pagename
    if fallback_prefix is None:
        raise WikiPrefixNotProvided
    else:
        return fallback_prefix, absolute_pagename

def join_pagename(prefix, pagename):
    "Convert prefix + pagename to absolute_pagename"
    return u'%s:%s' % (prefix, pagename)
