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

from django import newforms as forms
from ductus.apps.urn import get_resource_database
from ductus.urn import UnsupportedURN

# should UnsupportedURN in the lower level just really return a KeyError?

class PictureUrnField(forms.CharField):
    def clean(self, value):
        value = super(PictureUrnField, self).clean(value)

        # Does it exist, and is it a picture?
        try:
            elt_tag = get_resource_database().get_xml_tree(value).getroot().tag
            if elt_tag == '{http://wikiotics.org/ns/2008/picture}picture':
                return value
        except KeyError:
            pass
        # Fixme: we should probably give more specific error responses
        raise forms.ValidationError('Not a valid picture in the system')
