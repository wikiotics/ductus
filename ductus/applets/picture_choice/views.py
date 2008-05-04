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
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database

from random import shuffle

@register_view('{http://wikiotics.org/ns/2008/picture_choice}picture_choice', None)
def view_picture_choice(request, requested_view, urn, tree):
    root = tree.getroot()
    phrase = root.find('{http://wikiotics.org/ns/2008/picture_choice}phrase').text

    pictures = root.findall('.//{http://wikiotics.org/ns/2008/picture_choice}picture')
    pictures = [picture.get('{http://www.w3.org/1999/xlink}href')
                for picture in pictures]
    shuffle(pictures)

    object = {
        'pictures': pictures,
        'phrase': phrase,
    }

    return render_to_response('picture_choice.html',
                              {'object': object})
