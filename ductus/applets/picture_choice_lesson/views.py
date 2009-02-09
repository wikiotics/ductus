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
from django.template.loader import render_to_string
from django.template import RequestContext

from ductus.util.http import query_string_not_found
from ductus.wiki.decorators import register_view
from ductus.wiki import get_resource_database, SuccessfulEditRedirect
from ductus.applets.picture_choice_lesson.models import PictureChoiceLesson

@register_view(PictureChoiceLesson, None)
def view_picture_choice_lesson(request):
    questions = request.ductus.resource.questions.get_hrefs()
    frame = int(request.GET.get('frame', 0))
    if frame >= len(questions):
        return query_string_not_found(request)
    question = questions[frame]

    from ductus.applets.picture_choice.views import view_picture_choice
    qtree = get_resource_database().get_xml_tree(question)
    request.ductus.urn = question # VERY BAD!! (fixme asap)
    request.ductus.xml_tree = qtree # VERY BAD!! (fixme asap)
    return view_picture_choice(request)

@register_view(PictureChoiceLesson, 'edit')
def edit_picture_choice_lesson(request):
    resource_database = get_resource_database()
    tree = request.ductus.xml_tree

    if request.method == 'POST':
        # right now we only allow appending of elements through a single form
        # field...
        from django.utils import simplejson as json
        try:
            append_list = request.POST['append_list'].replace("'", '"')
            urns = json.loads(append_list)
        except ValueError:
            raise
        else:
            # now we append each element of this list with an xlink in the
            # document tree, save the new tree, and return the new urn
            pcl = request.ductus.resource.copy()
            pcl.quiz.extend_hrefs(urns)
            urn = pcl.save()
            return SuccessfulEditRedirect(urn)

    questions = request.ductus.resource.questions.get_hrefs()
    quiz = [tmp_general_picture_choice(q)
            for q in questions]
    return render_to_response('picture_choice_lesson/edit.html',
                              {'quiz': quiz},
                              context_instance=RequestContext(request))

def tmp_general_picture_choice(urn):
    picture_choice = PictureChoice(urn)
    correct_picture = picture_choice.correct_picture
    pictures = [correct_picture.href]
    pictures += [p.href for p in picture_choice.incorrect_pictures]
    phrase = picture_choice.phrase

    object = {
        'pictures': pictures,
        'correct_picture': correct_picture,
        'phrase': phrase,
    }

    return object

@register_view(PictureChoiceLesson, 'tmp_json')
def tmp_json_picture_choice_lesson(request):
    questions = request.ductus.resource.questions.get_hrefs()
    return render_to_response('picture_choice_lesson/tmp_json.html',
                              {'questions': questions},
                              context_instance=RequestContext(request))

@register_view(PictureChoiceLesson, 'html_flashcards')
def html_flashcards(request):
    questions = request.ductus.resource.questions.get_hrefs()
    quiz = [tmp_general_picture_choice(q)
            for q in questions]
    return render_to_response('picture_choice_lesson/flashcards.html',
                              {'quiz': quiz},
                              context_instance=RequestContext(request))
