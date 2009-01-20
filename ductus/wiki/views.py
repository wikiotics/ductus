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

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.cache import patch_vary_headers, patch_cache_control
from ductus.wiki.models import WikiPage, WikiRevision
from ductus.urn.views import view_urn
from ductus.urn import SuccessfulEditRedirect

def view_wikipage(request, pagename):
    page = get_object_or_404(WikiPage, name=pagename)

    if request.GET.get('view', None) == 'location_history':
        response = render_to_response('wiki/location_history.html',
                                      {'page': page},
                                      context_instance=RequestContext(request))
        patch_vary_headers(response, ['Cookie', 'Accept-language'])
        return response

    revision = page.get_latest_revision() # what if none?
    hash_type, hash_digest = revision.urn.split(':')

    response = view_urn(request, hash_type, hash_digest, wikipage=True)

    if isinstance(response, SuccessfulEditRedirect):
        # the underlying page has been modified, so we should take note of that
        # and save its new location
        revision = WikiRevision(page=page, urn=response.urn[4:])
        if request.user.is_authenticated():
            revision.author = request.user
        else:
            revision.author_ip = request.remote_addr
        revision.save()

        return HttpResponseRedirect(request.path)

    patch_cache_control(response, must_revalidate=True)
    return response
