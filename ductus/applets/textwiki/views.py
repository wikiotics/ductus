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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database
from ductus.util.xml import make_ns_func
from ductus.apps.urn.util import resolve_urn, SuccessfulEditRedirect
from lxml import etree

nsmap = {None: 'http://wikiotics.org/ns/2008/wikitext'}
ns = make_ns_func(nsmap)

@register_view(ns('wikitext'), None)
def view_picture(request, requested_view, urn, tree):
    text = tree.getroot().find(ns('text')).text

    return render_to_response('textwiki/display_wiki.html',
                              {'text': text},
                              context_instance=RequestContext(request))

class WikiEditForm(forms.Form):
    textarea_attrs = {'cols': '80', 'rows': '30'}
    text = forms.CharField(widget=forms.Textarea(attrs=textarea_attrs))

@register_view(ns('wikitext'), 'edit')
def edit_picture(request, requested_view, urn, tree):
    if request.method == 'POST':
        form = WikiEditForm(request.POST)

        if form.is_valid():
            root = tree.getroot()
            root.find(ns('text')).text = form.cleaned_data['text']
            urn = get_resource_database().store_xml(etree.tostring(root))
            return SuccessfulEditRedirect(urn)

    else:
        form = WikiEditForm({'text': tree.getroot().find(ns('text')).text})

    return render_to_response('textwiki/edit_wiki.html',
                              {'form': form},
                              context_instance=RequestContext(request))
