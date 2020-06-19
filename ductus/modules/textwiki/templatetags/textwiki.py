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
from functools import wraps

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.utils.importlib import import_module
from django.utils import six
from django.conf import settings

from ductus.wiki.models import WikiPage
from ductus.wiki.namespaces import registered_namespaces
from ductus.modules.textwiki import internal_bodied_macros, internal_non_bodied_macros
from ductus.modules.textwiki.decorators import register_creoleparser_non_bodied_macro

register = template.Library()

def __get_dict_of_possible_module_variables(module_variable_dict):
    if not module_variable_dict:
        return None
    rv = {}
    for key, value in six.iteritems(module_variable_dict):
        if isinstance(value, six.string_types):
            mod_name, junk, var_name = value.rpartition('.')
            rv[key] = getattr(import_module(mod_name), var_name)
        else:
            rv[key] = value
    return rv

CREOLEPARSER_BODIED_MACROS = __get_dict_of_possible_module_variables(getattr(settings, "CREOLEPARSER_BODIED_MACROS", None))
CREOLEPARSER_NON_BODIED_MACROS = __get_dict_of_possible_module_variables(getattr(settings, "CREOLEPARSER_NON_BODIED_MACROS", None))

def __wiki_links_class_func(prefix):
    def _wiki_links_class_func(pagename):
        pagename = pagename.partition('#')[0].partition('?')[0]

        wns = registered_namespaces[prefix]
        if wns.page_exists(pagename):
            return "internal"
        else:
            return "internal broken"

    return _wiki_links_class_func

def create_image_path_func(original_path_func):
    @wraps(original_path_func)
    def image_path_func(pagename):
        pathname = original_path_func(pagename).partition('?')[0]
        return "%s?view=image&max_size=250,250" % pathname
    return image_path_func

__interwiki_links_base_urls = None
__interwiki_links_path_funcs = None
__interwiki_links_class_funcs = None
__bodied_macros = None
__non_bodied_macros = None

def __prepare_global_data_structures():
    global __interwiki_links_base_urls, __interwiki_links_path_funcs, __interwiki_links_class_funcs, __bodied_macros, __non_bodied_macros

    if __interwiki_links_base_urls is not None:
        return

    __interwiki_links_base_urls = {}
    __interwiki_links_path_funcs = {}
    __interwiki_links_class_funcs = {}
    for wns in six.itervalues(registered_namespaces):
        __interwiki_links_base_urls[wns.prefix] = u'/%s/' % wns.prefix
        __interwiki_links_path_funcs[wns.prefix] = (wns.path_func, create_image_path_func(wns.path_func))
        __interwiki_links_class_funcs[wns.prefix] = __wiki_links_class_func(wns.prefix)

        __bodied_macros = dict(internal_bodied_macros)
        if CREOLEPARSER_BODIED_MACROS:
            __bodied_macros.update(CREOLEPARSER_BODIED_MACROS)
        __non_bodied_macros = dict(internal_non_bodied_macros)
        if CREOLEPARSER_NON_BODIED_MACROS:
            __non_bodied_macros.update(CREOLEPARSER_NON_BODIED_MACROS)
    __interwiki_links_base_urls['DjangoBug'] = 'http://code.djangoproject.com/ticket/'
    __interwiki_links_base_urls['UbuntuBug'] = 'https://bugs.launchpad.net/ubuntu/+bug/'
    __interwiki_links_base_urls['enWP'] = 'http://en.wikipedia.org/wiki/'

@register.filter
@stringfilter
def creole(value, default_prefix=None):
    try:
        from creoleparser.core import Parser
        from creoleparser.dialects import create_dialect, creole11_base
    except ImportError:
        if settings.TEMPLATE_DEBUG:
            raise template.TemplateSyntaxError, "Error in {% creole %} filter: The Python creoleparser library isn't installed."
        return value
    else:
        __prepare_global_data_structures()
        default_prefix = default_prefix or u'en'
        parser_kwargs = {
            'wiki_links_base_url': '/%s/' % default_prefix,
            'no_wiki_monospace': True,
            'wiki_links_path_func': __interwiki_links_path_funcs[default_prefix],
            'wiki_links_class_func': __wiki_links_class_func(default_prefix),
            'interwiki_links_base_urls': __interwiki_links_base_urls,
            # on the next line, we copy the dict first because creoleparser's
            # create_dialect function modifies it inexplicably! (see
            # creoleparser issue #50)
            'interwiki_links_path_funcs': dict(__interwiki_links_path_funcs),
            'interwiki_links_class_funcs': __interwiki_links_class_funcs,
            'external_links_class': 'external',
            'disable_external_content': True,
            #'bodied_macros': __bodied_macros,
            #'non_bodied_macros': __non_bodied_macros,
        }
        creole2html = Parser(create_dialect(creole11_base, **parser_kwargs), encoding=None)

        return mark_safe(creole2html(value))

def register_html_macro(macro_name):
    def _register_html_macro(func):
        _registered_html_macros[macro_name] = func
        return func
    return _register_html_macro

_registered_html_macros = {}

@register_html_macro('pagelist')
def html5_pagelist_macro(macro_tag, fullpagesource):
    """ generate the html output for the pagelist macro"""

    from lxml import etree
    from ductus.resource.ductmodels import tag_value_attribute_validator
    from ductus.index import search_pages

    tags = macro_tag.get("data-tags", '')

    try:
        parsed_tags = tags.split(',')
        for tag in parsed_tags:
            tag_value_attribute_validator(tag)
    except Exception:
        rv = etree.fromstring('<p>Invalid tag search</p>')

    try:
        pages = search_pages(tags=parsed_tags)
    except Exception:
        rv = etree.fromstring('<p>Search failed</p>')

    rv = etree.Element('ul')
    rv.set("class", "search_results")
    for page in pages:
        li = etree.SubElement(rv, 'li')
        a = etree.SubElement(li, 'a', href=page['path'])
        a.text = page['absolute_pagename']

    return macro_tag.append(rv)

@register.filter
@stringfilter
def process_macros(html_input):
    """
    A template tag that processes a "ductus-html5" string into viewable html5.
    For now, it only runs macros.
    """

    from lxml import etree, cssselect
    source = etree.HTML(html_input)
    macro_tags = cssselect.CSSSelector('div.ductus-macro')(source)
    for mt in macro_tags:
        macro_name = mt.get('data-macro-name')
        try:
            mt = _registered_html_macros[macro_name](mt, source)
        except KeyError:
            pass    # macros are simply <div> tags in the input, fail silently if we don't know how to process them

    return mark_safe(etree.tostring(source))

__title_re = re.compile(r'^\s*=+\s*(.*?)\s*=*\s*$', re.MULTILINE | re.UNICODE)

@register.filter
@stringfilter
def creole_guess_title(value):
    s = __title_re.search(value)
    if s:
        return s.group(1)
    else:
        return u''

@register_creoleparser_non_bodied_macro('PageList')
def search_pages_macro(macro, environ, **kwargs):
    """
    A creole macro that lists wiki pages according to various criteria (tags only for now).
    Usage: <<PageList tags=tag1,tag2,tag3>>
    """
    from genshi import Markup
    from ductus.resource.ductmodels import tag_value_attribute_validator
    from ductus.index import search_pages

    tags = kwargs.get("tags", '')

    try:
        parsed_tags = tags.split(',')
        for tag in parsed_tags:
            tag_value_attribute_validator(tag)
    except Exception:
        return Markup('<p>Invalid tag search</p>')

    try:
        pages = search_pages(tags=parsed_tags)
    except Exception:
        return Markup('<p>Search failed</p>')

    html = ['<ul>']
    for page in pages:
        html.append('<li><a href="{0}">{1}</a></li>'.format(page['path'], page['absolute_pagename']))

    html.append('</ul>')
    return Markup('<p class="search_results">' + '\n'.join(html) + '</p>')
