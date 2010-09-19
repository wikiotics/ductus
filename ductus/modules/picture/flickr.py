# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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
import json

import flickrapi
from django.conf import settings

class FlickrJSON(flickrapi.FlickrAPI):
    """FlickrAPI with parsed JSON as the default format"""

    def __getattr__(self, name):
        # FlickrAPI is an old-style class as late as flickrapi 1.2
        a = flickrapi.FlickrAPI.__getattr__(self, name)
        if not callable(a):
            return a
        def f(*args, **kwargs):
            if kwargs.get("format", "json") != "json":
                return a(*args, **kwargs)
            kwargs.update(format="json", nojsoncallback=1)
            j = json.loads(a(*args, **kwargs))
            if j['stat'] != 'ok':
                raise flickrapi.exceptions.FlickrError(
                    u"Error: %(code)s: %(message)s" % j
                )
            return j
        return f

flickr = FlickrJSON(settings.DUCTUS_FLICKR_API_KEY)

def lazy_memoize(f):
    """Returns an object that when called returns the value of the given function.

    On each subsequent call the cached value is simply returned.
    """
    class ValueHolder(object):
        __slots__ = "v"
    rv = ValueHolder()
    def _memoize():
        if not hasattr(rv, "v"):
            rv.v = f()
        return rv.v
    return _memoize

license_map = lazy_memoize(lambda: dict([(x['id'], x['url']) for x in flickr.photos_licenses_getInfo()["licenses"]["license"] if x['url'] in settings.DUCTUS_ALLOWED_LICENSES]))

valid_sort_methods = {
    'date-posted-desc': 'Newest',
    'interestingness-desc': 'Most "interesting"',
    'interestingness-asc': 'Least "interesting"',
    'relevance': 'Most "relevant"',
}

url_format_map = {
    'square': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_s.jpg',
    'thumbnail': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_t.jpg',
    'small': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_m.jpg',
    'medium': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s.jpg',
    'large': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s_b.jpg',
    'original': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(originalsecret)s_o.%(originalformat)s',
    'page': 'http://www.flickr.com/photos/%(owner_id)s/%(id)s',
    'userpage': 'http://www.flickr.com/people/%(owner_id)s/',
}

class FlickrPhoto(object):
    """Initialized with a JSON photo, turns it into a nice little object"""

    def __init__(self, d):
        self.dict = dict(d)

        # we want a license url, not flickr's enumeration
        self.dict["license"] = license_map().get(self.dict["license"], None)

        # normalize results from photos.getInfo and photos.search
        try:
            self.dict["owner_id"] = self.dict["owner"]["nsid"]
        except (TypeError, KeyError):
            self.dict["owner_id"] = self.dict["owner"]

        # add list of urls for convenience
        for k, v in url_format_map.iteritems():
            try:
                self.dict[k + "_url"] = v % self.dict
            except KeyError:
                # fail safely for photo sizes that may not be given
                if k in ('original', 'large'):
                    self.dict[k + "_url"] = None
                else:
                    raise

    def __getitem__(self, key):
        return self.dict[key]

    def __getattr__(self, key):
        return self.dict[key]

# Everything below is for the flickr uri handler

from urllib2 import urlopen

from django import forms
from django.utils.translation import ugettext_lazy, ugettext as _

from ductus.modules.picture.forms import PictureImportForm
from ductus.modules.picture.models import Picture
from ductus.util import iterate_file_object

@PictureImportForm.register_uri_handler
class FlickrUriHandler(object):
    _uri_re = re.compile(r'http\://[A-Za-z\.]*flickr\.com/photos/[A-Za-z0-9_\-\.@]+/([0-9]+)')

    verbose_description = ugettext_lazy("a URL from Flickr")

    @classmethod
    def handles(cls, uri):
        return bool(cls._uri_re.match(uri))

    def __init__(self, uri):
        self.uri = uri

    def validate(self):
        picture_id = self._uri_re.match(self.uri).group(1)
        photo = FlickrPhoto(flickr.photos_getInfo(photo_id=picture_id)["photo"])
        if photo["media"] != "photo":
            raise forms.ValidationError(_("must be a photo, not '%s'" % photo["media"]))
        if photo["license"] is None:
            raise forms.ValidationError(_("This photo is not available under an acceptable license for this wiki."))
        self.photo = photo

    def save(self, save_context, picture=None, return_before_saving=False):
        photo = self.photo
        if picture is None:
            picture = Picture()
        img_url = photo.original_url or photo.large_url or photo.medium_url
        picture.blob.store(iterate_file_object(urlopen(img_url)))
        picture.blob.mime_type = 'image/jpeg'
        license_elt = picture.common.licenses.new_item()
        license_elt.href = photo['license']
        picture.common.licenses.array = [license_elt]
        picture.common.patch_from_blueprint(None, save_context)
        picture.credit.title.text = photo['title']['_content']
        picture.credit.original_url.href = photo.page_url
        picture.credit.author.text = "%(realname)s (%(username)s)" % photo['owner']
        picture.credit.author_url.href = photo.userpage_url
        if photo['rotation'] and photo.original_url:
            picture.rotation = unicode(360 - int(photo['rotation']))
        if return_before_saving:
            return
        return picture.save()
