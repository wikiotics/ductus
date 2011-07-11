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
from ductus.modules.picture.ductmodels import Picture
from ductus.modules.audio.ductmodels import Audio

_ns = 'http://wikiotics.org/ns/2009/picture_choice'

class PictureChoiceElement(ductmodels.Element):
    ns = _ns
    nsmap = {'picture_choice': ns}

    phrase = ductmodels.TextElement()
    picture = ductmodels.ResourceElement(Picture)

    audio = ductmodels.OptionalResourceElement(Audio)

@register_ductmodel
class PictureChoiceGroup(ductmodels.DuctModel):
    ns = _ns
    nsmap = {'picture_choice': ns}

    group = ductmodels.ArrayElement(PictureChoiceElement(), min_size=4, max_size=4)

@register_ductmodel
class PictureChoiceLesson(ductmodels.DuctModel):
    ns = _ns
    nsmap = {'picture_choice': ns}

    groups = ductmodels.ArrayElement(ductmodels.ResourceElement(PictureChoiceGroup))
