# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
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

from ductus.wiki.decorators import register_creation_view, register_view
from ductus.wiki import get_writable_directories_for_user
from ductus.modules.flashcards.ductmodels import FlashcardDeck
from ductus.wiki.views import handle_blueprint_post

@register_creation_view(FlashcardDeck)
@register_view(FlashcardDeck, 'edit')
@register_view(FlashcardDeck)
def edit_flashcard_deck(request):
    if request.method == 'POST':
        return handle_blueprint_post(request, FlashcardDeck)

    return render_to_response('flashcards/edit_flashcard_deck.html', {
        'writable_directories': get_writable_directories_for_user(request.user),
    }, RequestContext(request))

@register_view(FlashcardDeck, 'tmp_choice')
def choice(request):
    return render_to_response('flashcards/choice.html', {
    }, RequestContext(request))
