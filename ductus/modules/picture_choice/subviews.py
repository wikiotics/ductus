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

from ductus.wiki.subviews import register_subview, subview
from ductus.modules.picture_choice.models import PictureChoiceLesson

@register_subview(PictureChoiceLesson, 'subresources')
def subresources(resource):
    s = set()
    for pcg in [g.get() for g in resource.groups]:
        s.update([pce.picture.href for pce in pcg.group])
    return s
