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
from django.utils.translation import ugettext_lazy, ugettext as _

from ductus.wiki.decorators import register_creation_view, register_view, register_mediacache_view
from ductus.wiki import get_writable_directories_for_user
from ductus.wiki.views import handle_blueprint_post
from ductus.util.http import query_string_not_found
from ductus.util.bcp47 import language_tag_to_description
from ductus.modules.flashcards.ductmodels import FlashcardDeck, Flashcard, ChoiceInteraction, AudioLessonInteraction, StoryBookInteraction
from ductus.modules.flashcards.decorators import register_interaction_view
from ductus.modules.flashcards import registered_interaction_views
from ductus.modules.audio.views import get_joined_audio_mediacache_url, mediacache_cat_audio

def choice_flashcard_template(headings, prompt, answer):
    deck = FlashcardDeck()

    # set up headings
    for heading in headings:
        new_heading = deck.headings.new_item()
        new_heading.text = heading
        deck.headings.array.append(new_heading)

    # set up a default interaction
    ci = ChoiceInteraction()
    ci.prompt = str(prompt)
    ci.answer = str(answer)
    deck.interactions.array.append(deck.interactions.new_item())
    deck.interactions.array[0].store(ci, False)

    # create four empty rows (for now, at least)
    for i in xrange(4):
        card = Flashcard()
        for j in xrange(len(headings)):
            card.sides.array.append(card.sides.new_item())

        new_card = deck.cards.new_item()
        new_card.store(card, False)
        deck.cards.array.append(new_card)

    return deck

def picture_choice_flashcard_template():
    return choice_flashcard_template((_('Phrase'), _('Picture'), _('Audio')), prompt="0,2", answer="1")

def phrase_choice_flashcard_template():
    return choice_flashcard_template((_('Prompt'), _('Answer')), prompt="0", answer="1")

def podcast_flashcard_template():
    """return a template flashcard deck object for an empty podcast lesson"""
    deck = FlashcardDeck()

    # set up headings
    for heading in (_('Phrase'), _('Audio'), _('Speaker')):
        new_heading = deck.headings.new_item()
        new_heading.text = heading
        deck.headings.array.append(new_heading)

    # set up default audio interaction
    ali = AudioLessonInteraction()
    ali.audio = "1"
    ali.transcript = "0"
    deck.interactions.array.append(deck.interactions.new_item())
    deck.interactions.array[0].store(ali, False)

    # create an empty row
    card = Flashcard()
    for j in xrange(3):
        card.sides.array.append(card.sides.new_item())

    new_card = deck.cards.new_item()
    new_card.store(card, False)
    deck.cards.array.append(new_card)

    return deck

flashcard_templates = {
    'picture_choice': picture_choice_flashcard_template,
    'phrase_choice': phrase_choice_flashcard_template,
    'podcast': podcast_flashcard_template,
}

@register_creation_view(FlashcardDeck, description=ugettext_lazy('a flexible lesson type arranged as a series of flashcards in a grid'), category='lesson')
@register_view(FlashcardDeck, 'edit')
def edit_flashcard_deck(request):
    if request.method == 'POST':
        return handle_blueprint_post(request, FlashcardDeck)

    resource_or_template = None
    if hasattr(request, 'ductus') and getattr(request.ductus, 'resource', None):
        resource_or_template = request.ductus.resource
    elif request.GET.get('template') in flashcard_templates:
        resource_or_template = flashcard_templates[request.GET['template']]()

    return render_to_response('flashcards/edit_flashcard_deck.html', {
        'writable_directories': get_writable_directories_for_user(request.user),
        'resource_or_template': resource_or_template,
    }, RequestContext(request))

@register_view(FlashcardDeck)
def view_flashcard_deck(request):
    interactions_array = request.ductus.resource.interactions.array

    if not interactions_array:
        return edit_flashcard_deck(request)

    try:
        interaction = interactions_array[int(request.GET.get('interaction', 0))]
    except (ValueError, IndexError):
        return query_string_not_found(request)
    else:
        interaction = interaction.get()
        interaction_view = registered_interaction_views[interaction.fqn]
        return interaction_view(request, interaction)

def get_target_language_from_tags(request):
    """find target language of a lesson from its tags"""
    language_code = language_name = None
    if hasattr(request.ductus.resource, 'tags'):
        for tag in request.ductus.resource.tags:
            split = tag.value.split(':')
            if split[0] == 'target-language':
                language_code = split[1]
                break
    if language_code is not None:
        try:
            language_name = language_tag_to_description(language_code)
        except KeyError:
            pass

    return {'code': language_code, 'name': language_name}

@register_interaction_view(ChoiceInteraction)
def choice(request, interaction):
    """
    Display a flashcard deck that has a ChoiceInteraction as a quiz
    """
    return render_to_response('flashcards/choice.html', {
        'prompt_columns': [int(a) for a in interaction.prompt.split(',')],
        'answer_column': int(interaction.answer),
        'target_language': get_target_language_from_tags(request)
    }, RequestContext(request))

def _get_audio_urns_in_column(flashcard_deck, column):
    cells = [card.get().sides.array[column] for card in flashcard_deck.cards]
    return [cell.href for cell in cells if cell.href]

@register_interaction_view(AudioLessonInteraction)
def podcast(request, interaction):
    column = int(interaction.audio)
    resource = request.ductus.resource
    audio_urns = _get_audio_urns_in_column(resource, column)
    podcast_webm_relative_url = get_joined_audio_mediacache_url(resource, audio_urns, 'audio/webm')
    podcast_m4a_relative_url = get_joined_audio_mediacache_url(resource, audio_urns, 'audio/mp4')

    return render_to_response('flashcards/audio_lesson.html', {
        'podcast_webm_relative_url': podcast_webm_relative_url,
        'podcast_m4a_relative_url': podcast_m4a_relative_url,
    }, RequestContext(request))

@register_mediacache_view(FlashcardDeck)
def mediacache_flashcard_deck(blob_urn, mime_type, additional_args, flashcard_deck):
    if mime_type in ('audio/webm', 'audio/mp4'):
        # figure out which column the audio is from
        from hashlib import sha1
        for column in xrange(len(flashcard_deck.headings)):
            audio_urn_list = _get_audio_urns_in_column(flashcard_deck, column)
            if sha1(' '.join(audio_urn_list)).hexdigest() == additional_args:
                break
        else:
            return None

        # concatenate the audio
        return mediacache_cat_audio(blob_urn, audio_urn_list, mime_type)

    return None
