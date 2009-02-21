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
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse

from ductus.wiki.decorators import register_view
from ductus.wiki import get_resource_database
from ductus.applets.picture_choice.models import PictureChoice

from random import shuffle

factorial = lambda n: reduce(lambda x, y: x * y, range(n, 1, -1))

@register_view(PictureChoice, None)
def view_picture_choice(request):
    element = general_picture_choice(request.ductus.resource, request.GET)
    if request.is_ajax():
        return HttpResponse([element["html_block"]])
    else:
        return render_to_response('picture_choice/choice.html',
                                  {'element': element},
                                  context_instance=RequestContext(request))

def general_picture_choice(picture_choice, options_dict):
    correct_picture = picture_choice.correct_picture
    pictures = [correct_picture.href]
    pictures += [p.href for p in picture_choice.incorrect_pictures]
    phrase = picture_choice.phrase

    if 'order' in options_dict:
        pictures.sort()
        order = int(options_dict['order']) % factorial(len(pictures))
        new_pictures = []
        for n in range(len(pictures), 0, -1):
            i = order % n
            order //= n
            new_pictures.append(pictures[i])
            del pictures[i]
        pictures = new_pictures
    else:
        shuffle(pictures)

    object = {
        'pictures': pictures,
        'correct_picture': correct_picture.href,
        'phrase': phrase,
    }

    return {
        'html_block': render_to_string('picture_choice/element.html',
                                       {'object': object}),
    }
