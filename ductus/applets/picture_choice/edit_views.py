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

from django import newforms as forms
from django.shortcuts import render_to_response
from ductus.apps.urn import get_resource_database
from ductus.util.xml import add_simple_xlink, make_ns_func
from ductus.urn import UnsupportedURN

from lxml import etree

class PictureUrnField(forms.CharField):
    def clean(self, value):
        value = super(PictureUrnField, self).clean(value)

        # Does it exist, and is it a picture?
        try:
            elt_tag = get_resource_database().get_xml_tree(value).getroot().tag
            if elt_tag == '{http://wikiotics.org/ns/2008/picture}picture':
                return value
        except UnsupportedURN:
            pass
        raise forms.ValidationError('Not a valid picture in the system')

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
        d = self.data

        if not (d['phrase0'] or d['phrase1'] or d['phrase2'] or d['phrase3']):
            raise forms.ValidationError("Need at least one phrase")

        pictures = [d['picture0'], d['picture1'], d['picture2'], d['picture3']]
        pictures = [p for p in pictures if p]
        if len(set(pictures)) != len(pictures):
            raise forms.ValidationError("Pictures must be unique")

        return self.cleaned_data

def new_picture_choice(request):
    new_urns = []

    if request.method == 'POST':
        form = PictureChoiceForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            phrases = [cd['phrase0'], cd['phrase1'], cd['phrase2'],
                       cd['phrase3']]
            pictures = [cd['picture0'], cd['picture1'], cd['picture2'],
                        cd['picture3']]
            npictures = len(pictures)

            for n in range(len(phrases)):
                phrase = phrases[n]
                if phrase:
                    correct_picture = pictures[n]
                    incorrect_pictures = [pictures[m] for m in range(npictures)
                                          if m != n]
                    urn = save_picture_choice(phrase, correct_picture,
                                              incorrect_pictures)
                    new_urns.append(urn)

            form = PictureChoiceForm() # just do it all again!

    else:
        form = PictureChoiceForm()

    return render_to_response('picture_choice/new.html',
                              {'form': form,
                               'new_urns': new_urns})

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
