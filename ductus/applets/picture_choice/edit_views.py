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

from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from ductus.apps.urn import get_resource_database
from ductus.util.xml import add_simple_xlink, make_ns_func
from ductus.util.http import render_json_response
from ductus.applets.picture.forms import PictureUrnField

from lxml import etree

def all_unique(iterable):
    return len(frozenset(iterable)) == len(iterable)

def get_phrases(d):
    return (d['phrase0'], d['phrase1'], d['phrase2'], d['phrase3'])

def get_pictures(d):
    return (d['picture0'], d['picture1'], d['picture2'], d['picture3'])

class PictureChoiceForm(forms.Form):
    phrase0 = forms.CharField(required=False)
    picture0 = PictureUrnField()
    phrase1 = forms.CharField(required=False)
    picture1 = PictureUrnField()
    phrase2 = forms.CharField(required=False)
    picture2 = PictureUrnField()
    phrase3 = forms.CharField(required=False)
    picture3 = PictureUrnField()

    def clean(self):
        phrases = tuple(p for p in get_phrases(self.data) if p)
        if not phrases:
            raise forms.ValidationError("Need at least one phrase")
        if not all_unique(phrases):
            raise forms.ValidationError("Phrases must be unique")

        pictures = get_pictures(self.data)
        if not all_unique(pictures):
            raise forms.ValidationError("Pictures must be unique")

        return self.cleaned_data

def new_picture_choice(request):
    new_urns = []

    if request.method == 'POST':
        form = PictureChoiceForm(request.POST)

        if form.is_valid():
            phrases = get_phrases(form.cleaned_data)
            pictures = get_pictures(form.cleaned_data)

            for n in range(len(phrases)):
                phrase = phrases[n]
                if phrase:
                    incorrect = list(pictures)
                    correct = incorrect.pop(n)
                    urn = save_picture_choice(phrase, correct, incorrect)
                    new_urns.append(urn)

            view = request.GET.get('view', None)
            if view == 'json':
                return render_json_response({urns: new_urns})

            form = PictureChoiceForm() # just do it all again!

    else:
        form = PictureChoiceForm()

    return render_to_response('picture_choice/new.html',
                              {'form': form,
                               'new_urns': new_urns},
                              context_instance=RequestContext(request))

nsmap = {
    None: 'http://wikiotics.org/ns/2008/picture_choice',
    'xlink': 'http://www.w3.org/1999/xlink',
}
ns = make_ns_func(nsmap)

def save_picture_choice(phrase, correct_picture, incorrect_pictures):
    """returns urn of new picture choice"""

    root = etree.Element(ns('picture_choice'), nsmap=nsmap)
    etree.SubElement(root, ns('phrase')).text = phrase

    def add_pictures(elt, pictures):
        for picture in pictures:
            add_simple_xlink(etree.SubElement(elt, ns('picture')), picture)

    add_pictures(etree.SubElement(root, ns('correct')), [correct_picture])
    add_pictures(etree.SubElement(root, ns('incorrect')), incorrect_pictures)

    # save log of what we just did?

    return get_resource_database().store_xml(etree.tostring(root))
