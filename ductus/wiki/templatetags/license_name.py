# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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

from django.template.defaultfilters import stringfilter
from django.template import Library

from ductus.license import license_name_map

register = Library()

@register.filter
@stringfilter
def license_name(value):
    """Maps a license URI to a human-readable short title of the license.

    In the future, the returned string will automatically be translated
    into the current locale's language.
    """

    try:
        return license_name_map[value]
    except KeyError:
        return value
