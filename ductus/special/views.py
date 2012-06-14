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
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic.list_detail import object_list

from ductus.wiki.models import WikiRevision
from ductus.wiki.namespaces import BaseWikiNamespace, registered_namespaces, split_pagename

_special_page_dict = {}

# fixme: when doing the dict match, should we cutoff after the first slash (/) ?

def register_special_page(x):
    if isinstance(x, FunctionType):
        _special_page_dict[x.__name__] = x
    else:
        def _register(f):
            _special_page_dict[x] = f
            return f
        return _register

@register_special_page
def recent_changes(request, pagename):
    # fixme: also be able to query a certain page or something
    revisions = WikiRevision.objects.order_by('-timestamp')
    rss_url = request.escaped_full_path(view='rss')

    if request.GET.get('view') == 'rss':
        from django.contrib.syndication.views import Feed
        class RecentChangesFeed(Feed):
            title = u'Recent changes'
            link = rss_url
            description = u'Recent changes'

            def items(self):
                return revisions[:20]

            def item_title(self, item):
                return item.page.name

            def item_link(self, item):
                # get_absolute_url returns None when a page is deleted, so we
                # just link to the now/recently-empty page in that case
                return item.get_absolute_url() or item.page.get_absolute_url()

            def item_pubdate(self, item):
                return item.timestamp

        return RecentChangesFeed()(request)

    return object_list(request, queryset=revisions,
                       paginate_by=25,
                       extra_context={'rss_url': rss_url},
                       template_name='special/recent_changes.html',
                       template_object_name='revision')

@register_special_page
def version(request, pagename):
    from ductus import DUCTUS_VERSION
    from django.http import HttpResponse
    return HttpResponse("version %s" % DUCTUS_VERSION, content_type="text/plain")

@register_special_page
def user_count(request, pagename):
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    from django.db.models import F
    from django.utils.timezone import now
    from datetime import timedelta
    week_ago = now() - timedelta(days=7)
    statements = [
        "There are {0} registered users.".format(User.objects.count()),
        "{0} of those users have at some point returned to the site.".format(User.objects.filter(last_login__gt=(F('date_joined') + timedelta(days=1))).count()),
        "{0} have returned in the past week.".format(User.objects.filter(last_login__gte=week_ago).count()),
    ]
    return HttpResponse("\n".join(statements), content_type="text/plain")

__django_specialpages = (
    'create_account',
    'account_settings',
    'change_password',
    'reset_password',
    'login'
)
for __pagename in __django_specialpages:
    @register_special_page(__pagename)
    def __redirect_to_django_specialpage(request, pagename):
        return redirect('/' + pagename.replace('_', '-'))

@register_special_page
def search(request, pagename):
    from ductus.index import get_indexing_mongo_database
    indexing_db = get_indexing_mongo_database()
    if indexing_db is None:
        raise Http404("indexing database is not available")
    collection = indexing_db.urn_index

    # construct the mongodb query
    query = {}
    if 'tag' in request.GET:
        query["tags"] = {"$all": request.GET.getlist('tag')}

    if not query:
        # fixme: we should prompt the user for what they want to search
        raise Http404

    # perform the search
    query["current_wikipages"] = {"$not": {"$size": 0}}
    pages = collection.find(query, {"current_wikipages": 1})
    results = []
    for page in pages:
        absolute_pagename = page["current_wikipages"][0]
        prefix, pagename = split_pagename(absolute_pagename)
        try:
            wns = registered_namespaces[prefix]
        except KeyError:
            # for some reason there's a prefix we don't know about.  move
            # along.
            pass
        else:
            path = "/%s/%s" % (prefix, wns.path_func(pagename))
            results.append({
                "absolute_pagename": absolute_pagename,
                "path": path,
            })

    # return results to the user
    return render_to_response('special/search.html', {
        'results': results,
    }, RequestContext(request))

class SpecialPageNamespace(BaseWikiNamespace):
    def page_exists(self, pagename):
        return pagename in _special_page_dict

    def view_page(self, request, pagename):
        try:
            view_func = _special_page_dict[pagename]
        except KeyError:
            raise Http404

        response = view_func(request, pagename)

        # special pages expire immediately since they frequently change
        from django.utils.cache import patch_cache_control, patch_response_headers
        patch_response_headers(response, cache_timeout=0)
        patch_cache_control(response, must_revalidate=True)

        return response

SpecialPageNamespace('special')
