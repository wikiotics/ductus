# Ductus
# Copyright (C) 2010  Jim Garrison <garrison@wikiotics.org>
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

from ductus.wiki.subviews import register_subview
from ductus.modules.flashcards.ductmodels import Flashcard, FlashcardDeck, Phrase

@register_subview(Flashcard, 'subresources')
def flashcard_subresources(resource):
    s = set()
    s.update([side.href for side in resource.sides if side.href])
    return s

@register_subview(FlashcardDeck, 'subresources')
def flashcard_deck_subresources(fcd):
    s = set()
    for fc in fcd.cards:
        if not fc.href:
            continue
        #s.add(fc.href)
        s.update(flashcard_subresources(fc.get()))
    return s

@register_subview(Phrase, 'as_html')
def phrase_as_html(phrase):
    from django.utils.html import escape
    from django.utils.safestring import mark_safe
    return mark_safe('<div class="ductus_phrase">%s</div>' % escape(phrase.phrase.text))

@register_subview(FlashcardDeck, 'as_html')
def flashcard_as_html(flashcard_deck):
    flashcards = [card.get() for card in flashcard_deck.cards]
    headings = [heading.text for heading in flashcard_deck.headings]
    from django.template import Context, loader
    t = loader.get_template('flashcards/flashcard_deck_as_html.html')
    return t.render(Context({
        'flashcard_deck': flashcard_deck,
        'flashcards': flashcards,
        'headings': headings,
    }))
