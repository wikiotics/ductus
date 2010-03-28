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

import json

from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_view, register_creation_view
from ductus.util.http import render_json_response
from ductus.modules.picture.models import Picture
from ductus.modules.picture.forms import PictureUrnField
from ductus.modules.picture_choice.models import PictureChoiceGroup, PictureChoiceLesson

def all_unique(iterable):
    return len(frozenset(iterable)) == len(iterable)

def get_phrases(d):
    return (d['phrase0'], d['phrase1'], d['phrase2'], d['phrase3'])

def get_pictures(d):
    return (d['picture0'], d['picture1'], d['picture2'], d['picture3'])

class PictureChoiceGroupForm(forms.Form):
    phrase0 = forms.CharField()
    picture0 = PictureUrnField()
    phrase1 = forms.CharField()
    picture1 = PictureUrnField()
    phrase2 = forms.CharField()
    picture2 = PictureUrnField()
    phrase3 = forms.CharField()
    picture3 = PictureUrnField()

    def clean(self):
        if not all_unique(get_phrases(self.data)):
            raise forms.ValidationError("Phrases must be unique")

        picture_blob_urns = [Picture.load(urn).blob.href
                             for urn in get_pictures(self.data)]
        if not all_unique(picture_blob_urns):
            raise forms.ValidationError("Pictures must be unique")

        return self.cleaned_data

@register_creation_view(PictureChoiceGroup)
def new_picture_choice_group(request):
    new_urns = []

    if request.method == 'POST':
        form = PictureChoiceGroupForm(request.POST)

        if form.is_valid():
            pcg = PictureChoiceGroup()
            for phrase, picture in zip(get_phrases(form.cleaned_data),
                                       get_pictures(form.cleaned_data)):
                pc = pcg.group.new_item()
                pc.phrase.text = phrase
                pc.picture.href = picture
                pcg.group.array.append(pc)

            urn = pcg.save()
            return SuccessfulEditRedirect(urn)

    else:
        form = PictureChoiceGroupForm()

    if request.is_ajax():
        return HttpResponse(unicode(form))

    return render_to_response('picture_choice/new.html',
                              {'form': form},
                              context_instance=RequestContext(request))

@register_creation_view(PictureChoiceLesson)
def new_picture_choice_lesson(request):
    if request.method != "POST":
        return HttpResponse('<form method="post"><input type="submit" value="Click to create picture choice lesson"/></form>')
    urn = PictureChoiceLesson().save()
    return SuccessfulEditRedirect(urn)

@register_view(PictureChoiceLesson, 'edit')
def edit_picture_choice_lesson(request):
    if request.method == 'POST':
        try:
            urns = json.loads(request.POST['pcl'])['groups']
        except ValueError:
            raise
        else:
            # fixme: only save if something actually changes
            pcl = request.ductus.resource.clone()
            pcl.groups.array = []
            #pcl.groups.extend_hrefs(urns) # fixme: current api is clumsy
            for u in urns:
                g = pcl.groups.new_item()
                g.href = u
                pcl.groups.array.append(g)
            urn = pcl.save()
            return SuccessfulEditRedirect(urn)

    groups = [href.get() for href in request.ductus.resource.groups]
    return render_to_response('picture_choice/edit_lesson.html', {
        'groups': groups,
    }, RequestContext(request))

@register_view(PictureChoiceGroup, '_edit_lesson_li')
def list_items_for_edit_view(request):
    groups = [request.ductus.resource]
    return render_to_response('picture_choice/edit_lesson_li.html', {
        'groups': groups,
    }, RequestContext(request))
