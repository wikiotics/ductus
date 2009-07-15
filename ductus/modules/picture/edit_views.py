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
from functools import partial

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import QueryDict, HttpResponse
from django.core.paginator import Paginator

from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view, register_view
from ductus.util.http import render_json_response
from ductus.modules.picture.models import Picture
from ductus.modules.picture.flickr import flickr, FlickrPhoto, license_map, url_format_map, valid_sort_methods
from ductus.modules.picture.forms import PictureRotationForm, PictureImportForm

@register_creation_view(Picture)
def new_picture(request):
    if request.GET.get('view') == 'flickr_search':
        return flickr_search_view(request)

    if request.method == 'POST':
        form = PictureImportForm(request.POST)
        if form.is_valid():
            urn = form.save()
            return SuccessfulEditRedirect(urn)
    else:
        form = PictureImportForm()

    return render_to_response('picture/picture_import_form.html', {
        'form': form,
    }, RequestContext(request))

def flickr_search_view(request):
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
        search_photos = partial(flickr.photos_search, per_page=100,
                                license=(','.join(license_map())),
                                safe_search=1, content_type=1, media="photos",
                                extras="license,owner_name,original_format")

        if request.GET.get("sort", None) in valid_sort_methods:
            kw["sort"] = request.GET["sort"]
        if request.GET.get("search_by", None) == 'tags':
            tags = [t for t in re.split(r'\s|"(.+)"', request.GET['q']) if t]
            kw['tags'] = ','.join(tags)
        else:
            kw['text'] = request.GET['q']
        photos = search_photos(**kw)["photos"]
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
        'sort_method': kw.get('sort', 'date-posted-desc'),
    }, RequestContext(request))

@register_view(Picture, 'edit')
def edit_picture(request):
    if request.method == 'POST':
        form = PictureRotationForm(request.POST)
        if form.is_valid():
            picture = request.ductus.resource = request.ductus.resource.clone()
            picture.rotation = form.cleaned_data['rotation']
            urn = picture.save()
            return SuccessfulEditRedirect(urn)
    else:
        form = PictureRotationForm()

    return render_to_response('picture/edit.html', {
        'form': form,
    }, RequestContext(request))
