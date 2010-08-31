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

from django import template

register = template.Library()

class TitleNode(template.Node):
    def __init__(self, title):
        if (title[0] == title[-1] and title[0] in ('"', "'")):
            self.title = lambda context: title[1:-1]
        else:
            self.title = lambda context: context[title]
    def render(self, context):
        # Add to title_list in top-level context
        title_list = context.dicts[0].setdefault('title_list', [])
        if isinstance(title_list, list):
            new_title = self.title(context)
            # before appending, make sure it does not duplicate the most
            # recently added title
            if not (title_list and title_list[-1] == new_title):
                title_list.append(new_title)
        return ''

@register.tag
def title(parser, token):
    tag_name, title = token.split_contents()
    return TitleNode(title)
