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

import re

from django.http import HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from django.conf import settings

from ductus.resource import ResourceDatabase, UnsupportedURN, get_resource_database
from ductus.wiki.namespaces import registered_namespaces

__whitespace_re = re.compile(r'\s', re.UNICODE)

is_valid_urn = ResourceDatabase.is_valid_urn

def verify_valid_urn(urn):
    """Raises UnsupportedURN if invalid"""

    if not is_valid_urn(urn):
        raise UnsupportedURN(urn)

def resolve_urn(urn):
    """Resolves a URN, returning its absolute URL on the server"""

    verify_valid_urn(urn)
    return u'/%s' % u'/'.join(urn.split(':'))

class SuccessfulEditRedirect(HttpResponseRedirect):
    """Used by 'edit' views to say that an edit or fork has led to a new URN
    """

    handled = False

    def __init__(self, urn):
        self.urn = urn
        return HttpResponseRedirect.__init__(self, resolve_urn(urn))

    def set_redirect_url(self, url):
        self['Location'] = iri_to_uri(url)

def is_legal_wiki_pagename(prefix, pagename):
    """Call this before creating a new wikipage.

    In addition to doing various legality checks, this function returns False
    for special pages, since they aren't normal wiki pages (as they cannot be
    created or edited, and revisions are not stored in the system).
    """
    if not pagename:
        return False

    if pagename[0] in (u'/', u'_') or pagename[-1] in (u'/', u'_'):
        # page names shouldn't begin or end with a slash or underscore
        return False

    if u'//' in pagename or u'__' in pagename:
        # page names shouldn't contain multiple adjacent slashes or underscores
        return False

    if u'/_' in pagename or u'_/' in pagename:
        # a portion of the path should not begin or end with an underscore
        return False

    if __whitespace_re.search(pagename):
        # pages should not contain spaces.  use underscores instead.
        return False

    # make sure the namespace exists and allows page creation
    try:
        wns = registered_namespaces[prefix]
    except KeyError:
        return False

    return wns.allow_page_creation

def user_has_edit_permission(user, prefix, pagename):
    """Does the given user have permission to edit an existing wiki page?

    If you are creating a new page, you should call `is_legal_wiki_pagename`
    first.
    """
    assert(is_legal_wiki_pagename(prefix, pagename))

    if not pagename:
        return False

    try:
        wns = registered_namespaces[prefix]
    except KeyError:
        return False

    return wns.allow_edit(user, pagename)

def user_has_unlink_permission(user, prefix, pagename):
    """Can a user delete a given page?

    This function assumes that `pagename` is a legal pagename.

    Currently, the pagename already exists any time this function is called,
    but we do not rely on this assumption anywhere.  Maybe we will in the
    future, though.
    """
    assert is_legal_wiki_pagename(prefix, pagename)
    return user.is_authenticated() and user_has_edit_permission(user, prefix, pagename)

def get_writable_directories_for_user(user):
    """Each entry is a tuple (directory, directory_type, description)"""
    rv = []
    if user.is_authenticated():
        rv.append(('user:%s/' % user.username, 'user', user.username))
        rv.extend(('group:%s/' % group.slug, 'group', group.name)
                  for group in user.groups.all())
    rv.extend(('%s:' % lang, 'language_namespace', lang_name)
              for lang, lang_name in settings.DUCTUS_NATURAL_LANGUAGES)
    return tuple(rv)

registered_views = {}
registered_creation_views = {}
registered_subviews = {}
registered_mediacache_views = {}
