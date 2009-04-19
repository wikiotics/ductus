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

try:
    import json # added in python 2.6
except ImportError:
    from django.utils import simplejson as json

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
    'original': 'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(originalsecret)s_o.%(originalformat)s',
    'page': 'http://www.flickr.com/photos/%(owner_id)s/%(id)s',
    'userpage': 'http://www.flickr.com/people/%(owner_id)s/',
}

class FlickrPhotoMetaclass(type):
    """Adds square_url, thumbnail_url, etc properties to FlickrPhoto"""

    def __init__(cls, name, bases, attrs):
        def make_get_func(v):
            def _get(s):
                return v % s.dict
            return _get
        for k, v in url_format_map.iteritems():
            setattr(cls, k + "_url", property(make_get_func(v)))

class FlickrPhoto(object):
    """Initialized with a JSON photo, turns it into a nice little object"""

    __metaclass__ = FlickrPhotoMetaclass

    def __init__(self, d):
        self.dict = dict(d)
        # normalize results from photos.getInfo and photos.search
        try:
            self.dict["owner_id"] = self.dict["owner"]["nsid"]
        except (TypeError, KeyError):
            self.dict["owner_id"] = self.dict["owner"]

    def __getitem__(self, key):
        if key == "license":
            return license_map()[self.dict[key]]
        return self.dict[key]
