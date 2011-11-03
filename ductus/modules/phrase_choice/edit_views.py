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
from django.utils.translation import ugettext_lazy

from ductus.wiki.decorators import register_view, register_creation_view
from ductus.wiki.views import handle_blueprint_post
from ductus.modules.phrase_choice.ductmodels import PhraseChoiceLesson

@register_creation_view(PhraseChoiceLesson, description=ugettext_lazy('a phrase is displayed as a prompt with four other phrases as possible answers'), category='lesson')
@register_view(PhraseChoiceLesson, 'edit')
def edit_phrase_choice_lesson(request):
    if request.method == 'POST':
        return handle_blueprint_post(request, PhraseChoiceLesson)

    if hasattr(request, "ductus"):
        # set ourselves up to edit an existing lesson
        resource_json = {
            'href': request.ductus.resource.urn,
            'resource': request.ductus.resource.output_json_dict(),
        }
    else:
        # set ourselves up to create a new lesson
        resource_json = None

    return render_to_response('phrase_choice/edit_lesson.html', {
        'resource_json': resource_json,
    }, RequestContext(request))
