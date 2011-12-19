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

"""
This module allows us to have a series of titles and subtitles in the HTML
<title> element.

For instance, a lesson about Animals may have, in the <title> element, 'Animals
- Example Ductus Site'.  Using this framework, we can add an arbitrary number
of subtitles and have them all displayed with the most specific first.

Ultimately, all these subtitles are put into the HTML <title> element in
ductus_base.html.
"""

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
    """Adds a title/subtitle to the list of titles that should be rendered on a page.

    This should be called in a specific order for each title: it should called
    given the most general (top-level) title first, and the final time it is
    called it should be given the most specific title.

    For instance, if this function is called twice while rendering a template:

    {% title "Example Ductus Site" %}
    {% title "Animals" %}

    then the <title> of the page will be "Animals - Example Ductus Site".

    This function works by appending to a list which is stored in the top-level
    template context with variable name title_list.
    """
    tag_name, title = token.split_contents()
    return TitleNode(title)
