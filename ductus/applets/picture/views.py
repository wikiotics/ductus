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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database

from PIL import Image, ImageFile
from cStringIO import StringIO

ns = lambda s: ('{http://wikiotics.org/ns/2008/picture}%s' % s)

__allowed_thumbnail_sizes = set([(250, 250)])

@register_view(ns('picture'), None)
def view_picture_info(request, requested_view, urn, tree):
    return render_to_response('picture/display.html', {'urn': urn},
                              context_instance=RequestContext(request))

@register_view(ns('picture'), 'image')
def view_picture(request, requested_view, urn, tree):
    blob = tree.getroot().find(ns('blob'))
    blob_urn = blob.get('{http://www.w3.org/1999/xlink}href')
    mime_type = blob.get('type') # lxml does not seem to set the
                                 # namespace correctly on this element
                                 # when parsing.  Investigation is
                                 # needed.

    # fixme: set X-License header

    # prepare original image
    data_iterator = get_resource_database().get_blob(blob_urn)

    # resize if requested
    if 'max_size' in request.GET:
        try:
            max_width, max_height = [int(n) for n in
                                     request.GET['max_size'].split(',')]
        except Exception:
            raise # call this a formatting error or something
        if (max_width, max_height) not in __allowed_thumbnail_sizes:
            raise Exception("Requested size not available")

        p = ImageFile.Parser()
        for data in data_iterator:
            p.feed(data)
        im = p.close()
        im.thumbnail((max_width, max_height), Image.ANTIALIAS)
        output = StringIO()
        im.save(output, 'JPEG')
        data_iterator = iter([output.getvalue()])
        mime_type = 'image/jpeg'

    return HttpResponse(data_iterator,
                        content_type=mime_type)
