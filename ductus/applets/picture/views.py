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
from django.views.decorators.vary import vary_on_headers
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database
from ductus.util.xml import make_ns_func

from PIL import Image, ImageFile
from cStringIO import StringIO

nsmap = {
    None: 'http://wikiotics.org/ns/2008/picture',
    'xlink': 'http://www.w3.org/1999/xlink',
}
ns = make_ns_func(nsmap)

__allowed_thumbnail_sizes = set([(250, 250), (100, 100), (50, 50)])

@register_view(ns('picture'), None)
@vary_on_headers('Cookie', 'Accept-language')
def view_picture_info(request):
    return render_to_response('picture/display.html',
                              {'urn': request.ductus.urn},
                              context_instance=RequestContext(request))

@register_view(ns('picture'), 'image')
def view_picture(request):
    blob = request.ductus.xml_tree.getroot().find(ns('blob'))
    blob_urn = blob.get(ns('xlink', 'href'))
    mime_type = blob.get('type') # lxml does not seem to set the
                                 # namespace correctly on this element
                                 # when parsing.  Investigation is
                                 # needed.  My bad: it's not supposed to.

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

    return HttpResponse(list(data_iterator), # see django #6527
                        content_type=mime_type)
