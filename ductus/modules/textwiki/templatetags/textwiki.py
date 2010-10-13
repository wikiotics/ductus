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

import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.conf import settings

from ductus.wiki.models import WikiPage
from ductus.wiki.namespaces import registered_namespaces

register = template.Library()

def __wiki_links_class_func(prefix):
    def _wiki_links_class_func(pagename):
        pagename = pagename.partition('#')[0].partition('?')[0]

        wns = registered_namespaces[prefix]
        if wns.page_exists(pagename):
            return "internal"
        else:
            return "internal broken"

    return _wiki_links_class_func

__interwiki_links_base_urls = None
__interwiki_links_path_funcs = None

def __prepare_interwiki_links_dicts():
    global __interwiki_links_base_urls, __interwiki_links_path_funcs

    if __interwiki_links_base_urls is not None:
        return

    __interwiki_links_base_urls = {}
    __interwiki_links_path_funcs = {}
    for wns in registered_namespaces.itervalues():
        __interwiki_links_base_urls[wns.prefix] = u'/%s/' % wns.prefix
        __interwiki_links_path_funcs[wns.prefix] = wns.path_func

@register.filter
@stringfilter
def creole(value, default_prefix=None):
    try:
        from creoleparser.core import Parser
        from creoleparser.dialects import create_dialect, creole10_base
    except ImportError:
        if settings.TEMPLATE_DEBUG:
            raise template.TemplateSyntaxError, "Error in {% creole %} filter: The Python creoleparser library isn't installed."
        return value
    else:
        __prepare_interwiki_links_dicts()
        default_prefix = default_prefix or u'en'
        wns = registered_namespaces[default_prefix]
        parser_kwargs = {
            'wiki_links_base_url': '/%s/' % default_prefix,
            'no_wiki_monospace': True,
            'wiki_links_path_func': wns.path_func,
            'wiki_links_class_func': __wiki_links_class_func(default_prefix),
            'interwiki_links_base_urls': __interwiki_links_base_urls,
            'interwiki_links_path_funcs': __interwiki_links_path_funcs,
            'external_links_class': 'external',
            'disable_external_content': True,
        }
        creole2html = Parser(create_dialect(creole10_base, **parser_kwargs))

        return mark_safe(creole2html(value))

__title_left_re = re.compile(r'^[\s=]*', re.UNICODE)
__title_right_re = re.compile(r'[\s=]*$', re.UNICODE)

@register.filter
@stringfilter
def creole_guess_title(value):
    try:
        first_line = (a for a in value.splitlines() if a).next()
    except StopIteration:
        return ''
    title = __title_left_re.sub('', __title_right_re.sub('', first_line))
    return title
