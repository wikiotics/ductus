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
from ductus.wiki.namespaces import BaseWikiNamespace

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

class SpecialPageNamespace(BaseWikiNamespace):
    def page_exists(self, pagename):
        return pagename in _special_page_dict

    def view_page(self, request, pagename):
        try:
            view_func = _special_page_dict[pagename]
        except KeyError:
            raise Http404

        return view_func(request, pagename)

SpecialPageNamespace('special')
