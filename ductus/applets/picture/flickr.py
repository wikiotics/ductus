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

from functools import partial

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

# fixme: make initialization of license_map (and hence search_photos) lazy
flickr = FlickrJSON(settings.DUCTUS_FLICKR_API_KEY)

license_map = dict([(x['id'], x['url']) for x in flickr.photos_licenses_getInfo()["licenses"]["license"] if x['url'] in settings.DUCTUS_ALLOWED_LICENSES])
license_query = u','.join(license_map)

search_photos = partial(flickr.photos_search, license=license_query, safe_search=1, content_type=1, media="photos", extras="license,owner_name,original_format", per_page=100)

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
    'page': 'http://www.flickr.com/photos/%(owner)s/%(id)s',
    'userpage': 'http://www.flickr.com/people/%(owner)s/',
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
        try:
            # normalize results from photos.getInfo and photos.search
            self.dict["owner"] = self.dict["owner"]["nsid"]
        except (TypeError, KeyError):
            pass

    def __getitem__(self, key):
        if key == "license":
            return license_map[self.dict[key]]
        return self.dict[key]

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import QueryDict
from django.core.paginator import Paginator

def search_view(request):
    kw = {'page': request.GET.get("page", "1")}
    place_name = None
    if "place_id" in request.GET:
        kw["place_id"] = request.GET["place_id"]
    elif "place" in request.GET and request.GET["place"]:
        places = flickr.places_find(query=request.GET["place"])["places"]["place"]
        try:
            place = places[0]
        except IndexError:
            pass
        else:
            kw["place_id"] = place["place_id"]
            place_name = place["_content"]
    if "q" in request.GET:
        if request.GET.get("sort", None) in valid_sort_methods:
            kw["sort"] = request.GET["sort"]
        photos = search_photos(text=request.GET["q"], **kw)["photos"]
        paginator = Paginator(range(photos["pages"]), 1)
        page = int(photos["page"])
        page_obj = paginator.page(page)
        photos = photos['photo']
        photos = [FlickrPhoto(p) for p in photos if 'originalsecret' in p]
    else:
        photos = None
        paginator = Paginator([], 1)
        page_obj = None
        page = 0
    next_qs = request.GET.copy()
    next_qs['page'] = page + 1
    next_qs = next_qs.urlencode()
    prev_qs = request.GET.copy()
    prev_qs['page'] = page - 1
    prev_qs = prev_qs.urlencode()

    return render_to_response('picture/flickr/search.html', {
        'place': place_name,
        'photos': photos,
        'paginator': paginator,
        'page_obj': page_obj,
        'page': page, # why can't page_obj identify its page number?
        'next_query_string': next_qs,
        'previous_query_string': prev_qs,
    }, RequestContext(request))
