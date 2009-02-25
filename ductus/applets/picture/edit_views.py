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

# TODO: license saving
#       determine whether the default view should just show the image or license info too
#       which namespace to save license info in
#       what license info to save
#       intermediate "data model" class
#       allowed licenses

import re
from urllib2 import urlopen

from django.http import HttpResponse

from ductus.wiki import get_resource_database, SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view
from ductus.util import iterate_file_object
from ductus.util.http import render_json_response
from ductus.applets.picture.models import Picture
from ductus.applets.picture.flickr import flickr, FlickrPhoto

def download_flickr(url):
    rdb = get_resource_database()

    picture_id = re.match(r'http\://[A-Za-z\.]*flickr\.com/photos/[A-Za-z0-9_\-\.@]+/([0-9]+)', url).group(1)
    photo = FlickrPhoto(flickr.photos_getInfo(photo_id=picture_id)["photo"])
    blob_urn = rdb.store_blob(iterate_file_object(urlopen(photo.original_url)))

    picture = Picture()
    picture.resource_database = rdb
    picture.blob.href = blob_urn
    picture.blob.mime_type = 'image/jpeg'
    license_elt = picture.common.licenses.new_item()
    license_elt.href = photo['license']
    picture.common.licenses.array = [license_elt]
#    picture.common.creator = picture_info['creator']
#    picture.common.rights = picture_info['rights']
#    picture.common.original_url = photo.page_url
    # fixme: save log of what we just did ?
    # fixme: save creator/original_url info
    return picture.save()

@register_creation_view(Picture)
def new_picture(request):
    if request.method == 'POST':
        # TODO: plugin system to recognize URI style and fetch image
        uri = request.POST['uri']
        if uri.startswith('urn:'):
            urn = uri
            # make sure it's a picture
            picture = get_resource_database().get_resource_object(urn)
            if not isinstance(picture, Picture):
                raise Exception("not a valid picture")
        else:
            urn = download_flickr(uri)

        return SuccessfulEditRedirect(urn)

    else:
        return HttpResponse('<form method="post">Enter a URI: <input name="uri"/><input type="submit" /></form>')
