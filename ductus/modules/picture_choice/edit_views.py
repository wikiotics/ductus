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

from ductus.wiki.decorators import register_view, register_creation_view
from ductus.wiki.views import handle_blueprint_post
from ductus.modules.picture_choice.ductmodels import PictureChoiceLesson

@register_creation_view(PictureChoiceLesson)
@register_view(PictureChoiceLesson, 'edit')
def edit_picture_choice_lesson(request):
    if request.method == 'POST':
        return handle_blueprint_post(request)

    if hasattr(request, "ductus"):
        # set ourselves up to edit an existing lesson
        resource_json = {
            'href': request.ductus.resource.urn,
            'resource': request.ductus.resource.output_json_dict(),
        }
    else:
        # set ourselves up to create a new lesson
        resource_json = None

    from django.conf import settings
    DUCTUS_FLICKR_GROUP_ID = getattr(settings, "DUCTUS_FLICKR_GROUP_ID", None)

    return render_to_response('picture_choice/edit_lesson.html', {
        'resource_json': resource_json,
        'DUCTUS_FLICKR_GROUP_ID': DUCTUS_FLICKR_GROUP_ID,
    }, RequestContext(request))
