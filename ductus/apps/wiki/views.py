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

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ductus.apps.wiki.models import WikiPage, WikiRevision
from ductus.apps.urn.views import view_urn

def view_wikipage(request, pagename):
    page = get_object_or_404(WikiPage, name=pagename)
    revision = page.get_latest_revision() # what if none?
    hash_type, hash_digest = revision.urn.split(':')
    return view_urn(request, hash_type, hash_digest)
