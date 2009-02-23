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
from ductus.wiki.decorators import register_view, unvarying
from ductus.wiki import get_resource_database
from ductus.applets.picture.models import Picture

from PIL import Image, ImageFile
from cStringIO import StringIO

__allowed_thumbnail_sizes = set([(250, 250), (100, 100), (50, 50)])

@register_view(Picture, None)
def view_picture_info(request):
    return render_to_response('picture/display.html',
                              {'urn': request.ductus.resource.urn},
                              context_instance=RequestContext(request))

def adjust_orientation_from_exif(image):
    rotation_table = {6: 270, 8: 90}
    try:
        exif = image._getexif()
        if exif is not None:
            orientation = exif[274]
            image = image.rotate(rotation_table[orientation], expand=True)
    except KeyError:
        pass
    return image

@register_view(Picture, 'image')
@unvarying
def view_picture(request):
    picture = request.ductus.resource
    mime_type = picture.blob.mime_type
    data_iterator = picture.blob.iterate(get_resource_database()) # iter(picture.blob)

    # resize if requested
    if 'max_size' in request.GET:
        try:
            max_width, max_height = [int(n) for n in
                                     request.GET['max_size'].split(',')]
        except Exception:
            raise # call this a formatting error or something
        if (max_width, max_height) not in __allowed_thumbnail_sizes:
            # fixme: once we cache things, we can just return any image with a
            # smaller size in most cases
            raise Exception("Requested size not available")

        p = ImageFile.Parser()
        for data in data_iterator:
            p.feed(data)
        im = p.close()
        im = adjust_orientation_from_exif(im)
        im.thumbnail((max_width, max_height), Image.ANTIALIAS)
        output = StringIO()
        im.save(output, 'JPEG', quality=90) # PIL manual says avoid quality > 95
        mime_type = 'image/jpeg'
        data_iterator = iter([output.getvalue()])

    return HttpResponse(list(data_iterator), # see django #6527
                        content_type=mime_type)

from flickr import search_view
register_view(Picture, "search")(search_view)
