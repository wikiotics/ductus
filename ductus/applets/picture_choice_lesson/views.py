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

try:
    import json # python 2.6
except ImportError:
    from django.utils import simplejson as json

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext

from ductus.util.http import query_string_not_found
from ductus.wiki.decorators import register_view
from ductus.wiki import get_resource_database, SuccessfulEditRedirect
from ductus.applets.picture_choice_lesson.models import PictureChoiceLesson
from ductus.applets.picture_choice.views import general_picture_choice

@register_view(PictureChoiceLesson, None)
def view_picture_choice_lesson(request):
    questions = [q.href for q in request.ductus.resource.questions]
    if not questions:
        return query_string_not_found(request)
    pc = get_resource_database().get_resource_object(questions[0])
    element = general_picture_choice(pc)
    return render_to_response('picture_choice_lesson/lesson.html', {
        'element': element,
        'questions': questions,
        'json_questions': json.dumps(questions),
    }, context_instance=RequestContext(request))

@register_view(PictureChoiceLesson, 'edit')
def edit_picture_choice_lesson(request):
    resource_database = get_resource_database()

    if request.method == 'POST':
        # right now we only allow appending of elements through a single form
        # field...
        try:
            append_list = request.POST['append_list'].replace("'", '"')
            urns = json.loads(append_list)
        except ValueError:
            raise
        else:
            # now we append each element of this list with an xlink in the
            # document tree, save the new tree, and return the new urn
            pcl = request.ductus.resource.clone()
            #pcl.questions.extend_hrefs(urns) # fixme: current api is clumsy
            for u in urns:
                q = pcl.questions.new_item()
                q.href = u
                pcl.questions.array.append(q)
            urn = pcl.save()
            return SuccessfulEditRedirect(urn)

    questions = request.ductus.resource.questions
    quiz = [resource_database.get_resource_object(q.href) for q in questions]
    return render_to_response('picture_choice_lesson/edit.html',
                              {'quiz': quiz},
                              context_instance=RequestContext(request))

@register_view(PictureChoiceLesson, 'tmp_json')
def tmp_json_picture_choice_lesson(request):
    questions = request.ductus.resource.questions.get_hrefs()
    return render_to_response('picture_choice_lesson/tmp_json.html',
                              {'questions': questions},
                              context_instance=RequestContext(request))
