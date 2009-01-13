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

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

@register.filter
@stringfilter
def creole(value):
    try:
        from creoleparser.core import Parser
        from creoleparser.dialects import Creole10
    except ImportError:
        if settings.TEMPLATE_DEBUG:
            raise template.TemplateSyntaxError, "Error in {% creole %} filter: The Python creoleparser library isn't installed."
        return value

    def wiki_links_path_func(page_name):
        # append slash, allowing for query_string
        page_name = '%s/%s%s' % page_name.partition('?')

        # handle special pages
        if not page_name.startswith(('user/', 'group/', 'urn/')):
            page_name = 'wiki/' + page_name

        return page_name

    interwiki_links_base_urls = dict(enWP='http://en.wikipedia.org/wiki/')

    c = Creole10(use_additions=False,
                 no_wiki_monospace=True,
                 wiki_links_base_url='/',
                 wiki_links_path_func=wiki_links_path_func,
                 interwiki_links_base_urls=interwiki_links_base_urls)
    creole2html = Parser(c)

    return mark_safe(creole2html(value))
