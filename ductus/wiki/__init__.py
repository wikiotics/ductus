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

from django.http import HttpResponseRedirect
from django.utils.encoding import iri_to_uri

from ductus.resource import ResourceDatabase, UnsupportedURN, get_resource_database

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

    def __init__(self, urn):
        self.urn = urn
        return HttpResponseRedirect.__init__(self, resolve_urn(urn))

    def set_redirect_url(self, url):
        self['Location'] = iri_to_uri(url)

def user_has_edit_permission(user, pagename):
    if '/' not in pagename:
        return False

    permission_func = wiki_permissions.get(pagename.partition('/')[0],
                                           lambda user, pagename: False)
    return permission_func(user, pagename)

registered_views = {}
registered_creation_views = {}
wiki_permissions = {}

wiki_permissions['wiki'] = lambda user, pagename: True
