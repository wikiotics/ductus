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

from django import forms
from django.utils.safestring import mark_safe
from ductus.wiki import get_resource_database, resolve_urn, UnsupportedURN
from ductus.modules.picture.models import Picture

def urn_to_img_url(urn):
    try:
        return u'%s?view=image&amp;max_size=100,100' % resolve_urn(urn)
    except UnsupportedURN:
        return None

class PictureSelector(forms.TextInput):
    """Picture selection widget

    Requires static/modules/picture/js/picture_selector.js
    """

    # fixme: we should set some element of this class to make it clear it
    # depends on picture_selector.js.  And hopefully we can make including an
    # automatic phenomenon.

    # or we could just move the static js file to a string here...

    # also, we should do the same thing for CSS

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs = dict(attrs)
        if 'class' in attrs:
            attrs['class'] += u' %s' % 'ductus_picture_selector'
        else:
            attrs['class'] = 'ductus_picture_selector'
        form_field = super(PictureSelector, self).render(name, value, attrs)
        div_attrs = {'class': 'ductus_picture_selector',
                     'id': u'%s_selector' % attrs['id']}
        img = u'<img src="%s"/>' % (urn_to_img_url(value) or '/broken.png')
        return mark_safe(u'<div%s>%s%s<div></div></div>'
                         % (forms.util.flatatt(div_attrs), img, form_field))

        # img fixmes: put it in a 100x100 container; get a blank image

class PictureUrnField(forms.CharField):
    """Field for a Picture URN
    """

    widget = PictureSelector

    def clean(self, value):
        value = super(PictureUrnField, self).clean(value)

        # Does it exist, and is it a picture?
        try:
            obj = get_resource_database().get_resource_object(value)
            if isinstance(obj, Picture):
                return value
        except KeyError:
            pass
        # Fixme: we should probably give more specific error responses
        raise forms.ValidationError('Not a valid picture in the system')
