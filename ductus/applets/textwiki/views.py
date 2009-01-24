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

from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from ductus.urn.views import register_view
from ductus.urn import get_resource_database, SuccessfulEditRedirect
from ductus.util.xml import make_ns_func
from lxml import etree

nsmap = {None: 'http://wikiotics.org/ns/2008/wikitext'}
ns = make_ns_func(nsmap)

# fixme: in this default view, lower the cache time for when links changed from
# broken to unbroken and back
@register_view(ns('wikitext'), None)
@vary_on_headers('Cookie', 'Accept-language')
def view_textwiki(request):
    text = request.ductus.xml_tree.getroot().find(ns('text')).text

    return render_to_response('textwiki/display_wiki.html',
                              {'text': text},
                              context_instance=RequestContext(request))

class WikiEditForm(forms.Form):
    textarea_attrs = {'cols': '80', 'rows': '30'}
    text = forms.CharField(widget=forms.Textarea(attrs=textarea_attrs))

@register_view(ns('wikitext'), 'edit')
@vary_on_headers('Cookie', 'Accept-language')
def edit_textwiki(request):
    if request.method == 'POST':
        form = WikiEditForm(request.POST)

        if form.is_valid():
            if 'preview' in request.GET:
                pass # fixme
            root = request.ductus.xml_tree.getroot()
            root.find(ns('text')).text = form.cleaned_data['text'].replace('\r', '')
            urn = get_resource_database().store_xml_tree(root)
            return SuccessfulEditRedirect(urn)

    else:
        textnode = request.ductus.xml_tree.getroot().find(ns('text'))
        form = WikiEditForm({'text': textnode.text})

    return render_to_response('textwiki/edit_wiki.html',
                              {'form': form},
                              context_instance=RequestContext(request))
