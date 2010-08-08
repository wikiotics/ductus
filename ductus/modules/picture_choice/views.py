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

from random import shuffle

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from ductus.util.http import query_string_not_found
from ductus.wiki.decorators import register_view
from ductus.modules.picture_choice.models import PictureChoiceGroup, PictureChoiceLesson

@register_view(PictureChoiceGroup)
def view_picture_choice_group(request):
    return view_picture_choice_groups(request, [lambda: request.ductus.resource])

@register_view(PictureChoiceLesson)
def view_picture_choice_lesson(request):
    def get_func(g):
        return lambda: g.get()
    groups = [get_func(g) for g in request.ductus.resource.groups]
    if not groups:
        return render_to_response('picture_choice/empty_lesson.html', {
        }, context_instance=RequestContext(request))

    return view_picture_choice_groups(request, groups)

def view_picture_choice_groups(request, groups):
    nframes = len(groups) * 4
    frame = request.GET.get('frame', None)
    frames = None
    if frame is None:
        frames = range(nframes)
        if request.GET.get('order', None) == 'shuffle':
            shuffle(frames)
        else:
            # shuffle each group of 4 individually
            for i in range(0, nframes, 4):
                g = frames[i:i+4]
                shuffle(g)
                frames[i:i+4] = g
        frame = frames[0]
    else:
        try:
            frame = int(frame)
        except ValueError:
            frame = None
        if frame is None or frame < 0 or frame >= nframes:
            return query_string_not_found(request)

    pcg = groups[frame / 4]()
    picture_urns = [pc.picture.href for pc in pcg.group]
    correct = pcg.group.array[frame % 4]
    shuffle(picture_urns)

    object = {
        'picture_urns': picture_urns,
        'correct_picture_urn': correct.picture.href,
        'phrase': correct.phrase,
    }

    if request.is_ajax():
        template_name = 'picture_choice/element.html'
    else:
        if frames:
            template_name = 'picture_choice/lesson.html'
        else:
            template_name = 'picture_choice/choice.html'

    return render_to_response(template_name, {
        'object': object,
        'frames': frames,
    }, RequestContext(request))
