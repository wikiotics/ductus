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
from django.utils.translation import ugettext_lazy

from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view, register_view
from ductus.util.http import render_json_response
from ductus.resource.ductmodels import BlueprintSaveContext
from ductus.modules.picture.ductmodels import Picture
from ductus.modules.picture.flickr import flickr, FlickrPhoto, license_map, url_format_map, valid_sort_methods, FlickrUriHandler
from ductus.modules.picture.forms import PictureRotationForm, PictureImportForm

@register_creation_view(Picture, description=ugettext_lazy('a standalone image'))
def new_picture(request):
    if request.GET.get('view') == 'flickr_search':
        return flickr_search_view(request)

    if request.method == 'POST':
        form = PictureImportForm(request.POST)
        if form.is_valid():
            save_context = BlueprintSaveContext.from_request(request)
            urn = form.save(save_context)
            return SuccessfulEditRedirect(urn)
    else:
        form = PictureImportForm()

    verbose_descriptions = PictureImportForm.get_verbose_input_descriptions()

    return render_to_response('picture/picture_import_form.html', {
        'form': form,
        'verbose_descriptions': verbose_descriptions,
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
        if "group" in request.GET:
            kw['group_id'] = request.GET["group"]
        search_result = search_photos(**kw)["photos"]
        page = int(search_result["page"])
        pages = int(search_result["pages"])
        # if we're not searching in a specific group, only return results for
        # which we are allowed to download the original image.  see ductus
        # ticket #64 for explanation of why
        photos = [FlickrPhoto(p).dict for p in search_result['photo']
                  if 'group' in request.GET or 'originalsecret' in p]

        # if somebody entered a flickr url in the search box, return that image
        if FlickrUriHandler.handles(request.GET['q']):
            from django import forms
            handler = FlickrUriHandler(request.GET['q'])
            try:
                handler.validate()
            except forms.ValidationError:
                pass
            else:
                photos.insert(0, handler.photo.dict)
    else:
        photos = None
        page = 0
        pages = 0

    return render_json_response({
        'place': place_name,
        'photos': photos,
        'page': page,
        'pages': pages,
        'sort_method': kw.get('sort', 'date-posted-desc'),
    })

@register_view(Picture, 'edit')
def edit_picture(request):
    if request.method == 'POST':
        form = PictureRotationForm(request.POST)
        if form.is_valid() and "parent" in request.POST:
            save_context = BlueprintSaveContext.from_request(request)
            blueprint = {
                'resource': {
                    '@patch': request.POST["parent"],
                    'rotation': form.cleaned_data['rotation'],
                }
            }
            urn = Picture.save_blueprint(blueprint, save_context)
            return SuccessfulEditRedirect(urn)
    else:
        form = PictureRotationForm()

    return render_to_response('picture/edit.html', {
        'form': form,
        'parent_urn': request.ductus.resource.urn,
    }, RequestContext(request))
