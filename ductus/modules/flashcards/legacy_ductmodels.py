# Ductus
# Copyright (C) 2012  Jim Garrison <garrison@wikiotics.org>
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

from django.utils.six.moves import xrange

from ductus.resource import ductmodels, register_ductmodel
from ductus.modules.picture.ductmodels import Picture
from ductus.modules.audio.ductmodels import Audio

_phrase_choice_ns = 'http://wikiotics.org/ns/2011/phrase_choice'
_picture_choice_ns = 'http://wikiotics.org/ns/2009/picture_choice'

class PhraseChoiceElement(ductmodels.Element):
    ns = _phrase_choice_ns
    nsmap = {'phrase_choice': ns}

    prompt = ductmodels.TextElement()
    answer = ductmodels.TextElement()

@register_ductmodel
class PhraseChoiceGroup(ductmodels.DuctModel):
    ns = _phrase_choice_ns
    nsmap = {'phrase_choice': ns}

    group = ductmodels.ArrayElement(PhraseChoiceElement(), min_size=4, max_size=4)

@register_ductmodel
class PhraseChoiceLesson(ductmodels.DuctModel):
    ns = _phrase_choice_ns
    nsmap = {'phrase_choice': ns}

    groups = ductmodels.ArrayElement(ductmodels.ResourceElement(PhraseChoiceGroup))

    def legacy_ductmodel_conversion(self):
        from ductus.modules.flashcards.ductmodels import FlashcardDeck, Flashcard, ChoiceInteraction, Phrase

        fcd = FlashcardDeck()

        # set up the choice interaction
        ci = ChoiceInteraction()
        ci.prompt = "0"
        ci.answer = "1"
        fcd.interactions.array.append(fcd.interactions.new_item())
        fcd.interactions.array[0].store(ci, False)

        # set up each flashcard
        for group in self.groups:
            for element in group.get().group:
                prompt = Phrase()
                prompt.phrase.text = element.prompt.text

                answer = Phrase()
                answer.phrase.text = element.answer.text

                flashcard = Flashcard()
                flashcard.sides.array.append(flashcard.sides.new_item())
                flashcard.sides.array[0].store(prompt, False)
                flashcard.sides.array.append(flashcard.sides.new_item())
                flashcard.sides.array[1].store(answer, False)

                new_item = fcd.cards.new_item()
                new_item.store(flashcard, False)
                fcd.cards.array.append(new_item)

        # set up the headings
        for h in ("prompt", "answer"):
            new_item = fcd.headings.new_item()
            new_item.text = h
            fcd.headings.array.append(new_item)

        # always, always, always preserve the DuctusCommonElement
        fcd.common = self.common

        return fcd

class PictureChoiceElement(ductmodels.Element):
    ns = _picture_choice_ns
    nsmap = {'picture_choice': ns}

    phrase = ductmodels.TextElement()
    picture = ductmodels.ResourceElement(Picture)

    audio = ductmodels.OptionalResourceElement(Audio)

@register_ductmodel
class PictureChoiceGroup(ductmodels.DuctModel):
    ns = _picture_choice_ns
    nsmap = {'picture_choice': ns}

    group = ductmodels.ArrayElement(PictureChoiceElement(), min_size=4, max_size=4)

@register_ductmodel
class PictureChoiceLesson(ductmodels.DuctModel):
    ns = _picture_choice_ns
    nsmap = {'picture_choice': ns}

    groups = ductmodels.ArrayElement(ductmodels.ResourceElement(PictureChoiceGroup))

    def legacy_ductmodel_conversion(self):
        from ductus.modules.flashcards.ductmodels import FlashcardDeck, Flashcard, ChoiceInteraction, Phrase

        fcd = FlashcardDeck()

        # set up the choice interaction
        ci = ChoiceInteraction()
        ci.prompt = "0,2"
        ci.answer = "1"
        fcd.interactions.array.append(fcd.interactions.new_item())
        fcd.interactions.array[0].store(ci, False)

        # set up each flashcard
        for group in self.groups:
            for element in group.get().group:
                phrase = Phrase()
                phrase.phrase.text = element.phrase.text

                flashcard = Flashcard()
                for i in xrange(3):
                    flashcard.sides.array.append(flashcard.sides.new_item())
                flashcard.sides.array[0].store(phrase, False)
                flashcard.sides.array[1].href = element.picture.href
                flashcard.sides.array[2].href = element.audio.href

                new_item = fcd.cards.new_item()
                new_item.store(flashcard, False)
                fcd.cards.array.append(new_item)

        # set up the headings
        for h in ("phrase", "picture", "audio"):
            new_item = fcd.headings.new_item()
            new_item.text = h
            fcd.headings.array.append(new_item)

        # always, always, always preserve the DuctusCommonElement
        fcd.common = self.common

        return fcd
