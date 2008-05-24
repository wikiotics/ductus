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

from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database

from random import shuffle

ns = lambda s: ('{http://wikiotics.org/ns/2008/picture_choice}%s' % s)

factorial = lambda n: reduce(lambda x, y: x * y, range(n, 1, -1))

@register_view(ns('picture_choice'), None)
def view_picture_choice(request, requested_view, urn, tree):
    element = general_picture_choice(urn, tree, request.GET)
    return render_to_response('picture_choice.html', {'element': element})

def general_picture_choice(urn, tree, options_dict):
    root = tree.getroot()
    phrase = root.find(ns('phrase')).text

    pictures = root.findall('.//' + ns('picture'))
    pictures = [picture.get('{http://www.w3.org/1999/xlink}href')
                for picture in pictures]

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
        'phrase': phrase,
    }

    return {
        'html_block': render_to_string('picture_choice_element.html',
                                       {'object': object}),
        'js': render_to_string('picture_choice_element.js',
                               {'object': object}),
    }
