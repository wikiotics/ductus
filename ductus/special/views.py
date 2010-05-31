# Ductus
# Copyright (C) 2010  Jim Garrison <jim@garrison.cc>
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
from types import FunctionType

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from ductus.wiki.models import WikiRevision

__special_page_dict = {}
__special_page_re_list = []

# should we really have a whole directory (app) just for "special"?  i guess,
# because i can't figure out where else to put it

# fixme: when doing the dict match, should we cutoff after the first slash (/) ?

def view_special_page(request, pagename):
    "Main view which dispatches to the appropriate handle based on pagename"

    try:
        # first look in dict
        view_func = __special_page_dict[pagename]
    except KeyError:
        # then try re's (fixme)

        # else 404
        raise Http404

    return view_func(request, pagename)

def register_special_page(x):
    if isinstance(x, FunctionType):
        __special_page_dict[x.__name__] = x
    else:
        def _register(f):
            __special_page_dict[x] = f
            return f
        return _register

@register_special_page
def recent_changes(request, pagename):
    # fixme: we should probably just use a generic view here to get pagination
    # fixme: also be able to output rss
    # fixme: also be able to query a certain page or something
    revisions = WikiRevision.objects.order_by('-timestamp')[:20]
    return render_to_response('special/recent_changes.html', {
        'revisions': revisions,
    }, RequestContext(request))

@register_special_page
def version(request, pagename):
    from ductus import DUCTUS_VERSION
    from django.http import HttpResponse
    return HttpResponse("version %s" % DUCTUS_VERSION, content_type="text/plain")

# WhatLinksHere, MovePage, Random, Gadgets?, NewPages, Tags?, ListUsers, BlockList, Contributions, [group things], various user-related and "personal" pages (especially Preferences), BrokenRedirects, Cite?, BookSources, Block, Undelete

# http://en.wikipedia.org/wiki/Special_Pages#Available_special_pages
