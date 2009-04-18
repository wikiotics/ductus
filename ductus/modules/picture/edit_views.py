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

import re
from urllib2 import urlopen

from django.http import HttpResponse

from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view
from ductus.util import iterate_file_object
from ductus.util.http import render_json_response
from ductus.modules.picture.models import Picture
from ductus.modules.picture.flickr import flickr, FlickrPhoto

def download_flickr(url):
    picture_id = re.match(r'http\://[A-Za-z\.]*flickr\.com/photos/[A-Za-z0-9_\-\.@]+/([0-9]+)', url).group(1)
    photo = FlickrPhoto(flickr.photos_getInfo(photo_id=picture_id)["photo"])
    if photo["media"] != "photo":
        raise Exception("must be a photo, not '%s'" % photo["media"])

    picture = Picture()
    picture.blob.store(iterate_file_object(urlopen(photo.original_url)))
    picture.blob.mime_type = 'image/jpeg'
    license_elt = picture.common.licenses.new_item()
    license_elt.href = photo['license']
    picture.common.licenses.array = [license_elt]
    picture.credit.title.text = photo['title']['_content']
    picture.credit.original_url.href = photo.page_url
    picture.credit.author.text = "%(realname)s (%(username)s)" % photo['owner']
    picture.credit.author_url.href = photo.userpage_url
    if photo['rotation']:
        picture.rotation = unicode(360 - int(photo['rotation']))
    # fixme: save log of what we just did ?
    return picture.save()

@register_creation_view(Picture)
def new_picture(request):
    if request.method == 'POST':
        # TODO: plugin system to recognize URI style and fetch image
        uri = request.POST['uri']
        if uri.startswith('urn:'):
            urn = uri
            Picture.load(urn) # this line makes sure it's a picture
        else:
            urn = download_flickr(uri)

        return SuccessfulEditRedirect(urn)

    else:
        return HttpResponse('<form method="post">Enter a URI: <input name="uri"/><input type="submit" /></form>')
