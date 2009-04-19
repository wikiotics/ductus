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
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.conf import settings

from ductus.wiki.models import WikiPage

register = template.Library()

creole2html = None

def prepare_parser():
    global creole2html
    if creole2html is not None:
        return

    from creoleparser.core import Parser
    from creoleparser.dialects import create_dialect, creole10_base

    def wiki_links_path_func(page_name):
        page_name = iri_to_uri(urlquote(page_name))

        # handle special pages
        if not page_name.startswith(('user/', 'group/', 'urn/')):
            page_name = 'wiki/' + page_name

        return page_name

    def wiki_links_class_func(page_name):
        page_name = page_name.partition('#')[0].partition('?')[0]
        page_name = wiki_links_path_func(page_name) # handle special pages
        try:
            if WikiPage.objects.get(name=page_name).get_latest_revision().urn:
                return "internal"
        except Exception:
            pass
        return "internal broken"

    interwiki_links_base_urls = dict(
        DjangoBug='http://code.djangoproject.com/ticket/',
        UbuntuBug='https://bugs.launchpad.net/ubuntu/+bug/',
        enWP='http://en.wikipedia.org/wiki/',
    )

    c = create_dialect(creole10_base,
                       no_wiki_monospace=True,
                       wiki_links_base_url='/',
                       wiki_links_path_func=wiki_links_path_func,
                       wiki_links_class_func=wiki_links_class_func,
                       interwiki_links_base_urls=interwiki_links_base_urls)
    creole2html = Parser(c)

@register.filter
@stringfilter
def creole(value):
    try:
        prepare_parser()
    except ImportError:
        if settings.TEMPLATE_DEBUG:
            raise template.TemplateSyntaxError, "Error in {% creole %} filter: The Python creoleparser library isn't installed."
        return value
    else:
        return mark_safe(creole2html(value))
