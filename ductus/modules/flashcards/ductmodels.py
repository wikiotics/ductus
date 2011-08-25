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

from ductus.resource import ductmodels, register_ductmodel

# we import other models explicitly (until DuctModel supports interfaces)
from ductus.modules.picture.ductmodels import Picture
from ductus.modules.audio.ductmodels import Audio
@register_ductmodel
class Phrase(ductmodels.BaseDuctModel):
    ns = 'http://wikiotics.org/ns/2011/phrase'
    nsmap = {'phrase': ns}

    phrase = ductmodels.TextElement()
# end of other models

@register_ductmodel
class Flashcard(ductmodels.DuctModel):
    ns = 'http://wikiotics.org/ns/2011/flashcards'
    nsmap = {'flashcards': ns}

    sides = ductmodels.ArrayElement(ductmodels.OptionalResourceElement(Phrase, Picture, Audio))

    def validate(self, strict=True):
        super(Flashcard, self).validate(strict)

        if len(self.sides) == 0:
            raise ductmodels.ValidationError("a flashcard must have at least one side")

@register_ductmodel
class FlashcardDeck(ductmodels.DuctModel):
    ns = 'http://wikiotics.org/ns/2011/flashcards'
    nsmap = {'flashcards': ns}

    cards = ductmodels.ArrayElement(ductmodels.ResourceElement(Flashcard))
    headings = ductmodels.ArrayElement(ductmodels.TextElement())
    column_order = ductmodels.Attribute(optional=True)

    def validate(self, strict=True):
        super(FlashcardDeck, self).validate(strict)

        headings_length = len(self.headings)

        if headings_length == 0:
            raise ductmodels.ValidationError("there are no sides")

        if any(len(card.get().sides) != headings_length for card in self.cards):
            raise ductmodels.ValidationError("each card must have the same number of sides as headers given")

        nonempty_headings = [h.text for h in self.headings if h.text]
        if len(frozenset(nonempty_headings)) != len(nonempty_headings):
            raise ductmodels.ValidationError("all nonempty headings must be unique")
