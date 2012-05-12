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

from django.template import Context, loader

from ductus.wiki.subviews import register_subview
from ductus.modules.picture.ductmodels import Picture

@register_subview(Picture, 'license_info')
def license_info(resource):
    t = loader.get_template('picture/license_info.html')
    return t.render(Context({'resource': resource}))

@register_subview(Picture, 'as_html')
def as_html(resource):
    t = loader.get_template('picture/as_html.html')
    return t.render(Context({'resource': resource}))
