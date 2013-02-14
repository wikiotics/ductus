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

from functools import partial

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django import forms

from ductus.resource import get_resource_database
from ductus.wiki.decorators import register_view, register_creation_view
from ductus.wiki import SuccessfulEditRedirect, get_writable_directories_for_user
from ductus.wiki.namespaces import registered_namespaces, split_pagename, WikiPrefixNotProvided
from ductus.wiki.views import handle_blueprint_post
from ductus.modules.textwiki.ductmodels import Wikitext   # FIXME: drop useless class
from ductus.modules.textwiki.templatetags.textwiki import creole
from ductus.utils.bcp47 import language_tag_to_description

recaptcha = None
if hasattr(settings, "RECAPTCHA_PRIVATE_KEY"):
    from recaptcha.client import captcha as recaptcha

# fixme: in this default view, lower the cache time for when links change from
# broken to unbroken and back
@register_view(Wikitext)
def view_textwiki(request):
    return render_to_response('textwiki/display_wiki.html', {
        'text': request.ductus.resource.text,
        'natural_language': request.ductus.resource.blob.natural_language or None,
        'markup_language': request.ductus.resource.blob.markup_language,
    }, context_instance=RequestContext(request))

@register_creation_view(Wikitext, description=ugettext_lazy('a "regular" text-based wiki page, using wiki-creole as markup'))
@register_view(Wikitext, 'edit')
def edit_textwiki(request):

    resource_database = get_resource_database()

    if request.method == 'POST':
        handle_blueprint_post(request, Wikitext)

    resource = None
    if hasattr(request, 'ductus') and getattr(request.ductus, 'resource', None):
        resource = request.ductus.resource
        # handle old creole content: make it look like ductus-html5 so we can edit it
        # content is not saved to creole anymore, only to ductus-html5
        if resource.blob.markup_language == 'creole-1.0':
            resource.blob.markup_language = 'ductus-html5'
            resource.text = creole(resource.text, resource.blob.natural_language)

    return render_to_response('textwiki/edit_wiki.html', {
        'resource_json': resource,
        'writable_directories': get_writable_directories_for_user(request.user),
    }, context_instance=RequestContext(request))

new_textwiki = edit_textwiki

# this should be in index/views.py
from ductus.special.views import register_special_page
from ductus.index import search_pages, IndexingError
from ductus.utils.http import query_string_not_found, render_json_response
from django.http import Http404

@register_special_page('ajax/search-pages')
def ajax_search_pages(request, pagename):
    """return a JSON object containing the urls matching the query
    in the request, such that:
    TODO: document
    """
    # TODO: limit the number of results returned
    if request.method == 'GET':
        params = {}
        params['pagename'] = request.GET.get('pagename', '')
        params['tags'] = request.GET.getlist('tag', '')

        # special search feature to report all pages without tags
        if 'notags' in request.GET:
            params['notags'] = 1
            del params['tags']  # just to be extra sure

        urls = search_pages(**params)

        return render_json_response(urls)
