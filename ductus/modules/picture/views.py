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
from django.template import RequestContext

from ductus.util.http import query_string_not_found
from ductus.wiki.decorators import register_view, register_mediacache_view
from ductus.decorators import unvarying
from ductus.wiki.mediacache import mediacache_redirect
from ductus.modules.picture.ductmodels import Picture

from cStringIO import StringIO

__allowed_thumbnail_sizes = sorted([(250, 250), (100, 100), (50, 50)],
                                   reverse=True)

@register_view(Picture)
def view_picture_info(request):
    return render_to_response('picture/display.html',
                              context_instance=RequestContext(request))

@register_view(Picture, 'image')
@unvarying
def view_picture(request):
    picture = request.ductus.resource
    mime_type = picture.blob.mime_type

    # figure out size to send
    thumbnail_str = ''
    if 'max_size' in request.GET:
        try:
            max_width, max_height = [int(n) for n in
                                     request.GET['max_size'].split(',')]
        except ValueError:
            return query_string_not_found(request)

        try:
            thumbnail_size = iter(s for s in __allowed_thumbnail_sizes
                                  if s <= (max_width, max_height)).next()
        except StopIteration:
            # refuse to make a thumbnail this small
            return query_string_not_found(request)

        thumbnail_str = '_'.join(str(s) for s in thumbnail_size)
        if picture.rotation:
            thumbnail_str += '_' + picture.rotation

    return mediacache_redirect(request, picture.blob.href, 'image/jpeg',
                               thumbnail_str, picture)

def adjust_orientation_from_exif(image):
    rotation_table = {6: 270, 8: 90}
    try:
        exif = image._getexif()
        if exif is not None:
            orientation = exif[274]
            image = image.rotate(rotation_table[orientation], expand=True)
    except (KeyError, AttributeError):
        pass
    return image

@register_mediacache_view(Picture)
def mediacache_picture(blob_urn, mime_type, additional_args, picture):
    from PIL import Image, ImageFile

    # for now this code assumes all pictures are jpegs
    assert picture.blob.mime_type == 'image/jpeg'

    if picture.blob.href != blob_urn:
        return None
    if mime_type != 'image/jpeg':
        return None
    if additional_args:
        try:
            if picture.rotation:
                max_width, max_height, rotation = additional_args.split('_')
            else:
                max_width, max_height = additional_args.split('_')
                rotation = None
        except ValueError:
            return None
        allowed_sizes = ('_'.join(str(s) for s in x)
                         for x in __allowed_thumbnail_sizes)
        if '%s_%s' % (max_width, max_height) not in allowed_sizes:
            return None
        if picture.rotation and picture.rotation != rotation:
            return None

        max_width, max_height = int(max_width), int(max_height)

    data_iterator = iter(picture.blob)

    # resize or rotate if needed
    if additional_args:
        p = ImageFile.Parser()
        for data in data_iterator:
            p.feed(data)
        im = p.close()
        if picture.rotation in ('0', '90', '180', '270'):
            im = im.rotate(int(picture.rotation), expand=True)
        else:
            im = adjust_orientation_from_exif(im)
        im.thumbnail((max_width, max_height), Image.ANTIALIAS)
        if im.mode != "RGB":
            im = im.convert("RGB")
        output = StringIO()
        im.save(output, 'JPEG', quality=90) # PIL manual says avoid quality > 95
        return iter([output.getvalue()])

    # otherwise, just send it along
    else:
        return data_iterator
