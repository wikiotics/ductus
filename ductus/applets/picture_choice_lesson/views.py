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
from django.template import RequestContext, Context, loader
from django.http import HttpResponse

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
            urns = json.loads(request.POST['pcl'])['questions']
        except ValueError:
            raise
        else:
            # fixme: only save if something actually changes
            # fixme: have the model only allow valid picture_choice's
            pcl = request.ductus.resource.clone()
            pcl.questions.array = []
            #pcl.questions.extend_hrefs(urns) # fixme: current api is clumsy
            for u in urns:
                q = pcl.questions.new_item()
                q.href = u
                pcl.questions.array.append(q)
            urn = pcl.save()
            # fixme: successful-edit-redirect doesn't really make sense w/ ajax...
            return SuccessfulEditRedirect(urn)

    questions = request.ductus.resource.questions
    quiz_list_items = list_items(request, [q.href for q in questions])
    return render_to_response('picture_choice_lesson/edit.html',
                              {'quiz_list_items': quiz_list_items},
                              context_instance=RequestContext(request))

# fixme: static view
@register_view(PictureChoiceLesson, 'static_li')
def list_items_for_edit_view(request):
    urns = json.loads(request.GET['urns'])
    return HttpResponse(list_items(request, urns))

def list_items(request, urns):
    quiz = [get_resource_database().get_resource_object(q) for q in urns]
    t = loader.get_template('picture_choice_lesson/edit_li.html')
    return t.render(Context({'quiz': quiz}))
