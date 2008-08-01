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

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from ductus.resource import determine_header
from ductus.apps.urn import get_resource_database
from ductus.apps.urn.util import urn_linkify
from ductus.util import remove_adjacent_duplicates

def view_urn(request, hash_type, hash_digest):
    """Dispatches the appropriate view for a resource
    """

    urn = 'urn:%s:%s' % (hash_type, hash_digest)
    resource_database = get_resource_database()
    try:
        data_iterator = resource_database[urn]
    except KeyError:
        raise Http404
    header, data_iterator = determine_header(data_iterator)

    requested_view = request.GET.get('view', None)

    if requested_view == 'raw':
        return HttpResponse(list(data_iterator), # see django #6527
                            content_type='application/octet-stream')

    if header == 'blob':
        header, data_iterator = determine_header(data_iterator, False)
        return HttpResponse(list(data_iterator), # see django #6527
                            content_type='application/octet-stream')

    if header == 'xml':
        del data_iterator
        tree = resource_database.get_xml_tree(urn)
        root_tag_name = tree.getroot().tag
        try:
            f = __registered_views[root_tag_name][requested_view]
        except KeyError:
            try:
                f = __registered_views[None][requested_view]
            except KeyError:
                raise Http404
        return f(request, requested_view, urn, tree)

    raise Http404

def register_view(root_tag_name, *args):
    """Registers a URN view function.

    root_tag_name should include the namespace information.  Additional
    arguments specify which views are defined.  The default view is specified
    by passing 'None' as an argument.
    """

    if len(args) == 0:
        raise TypeError("function requires at least two arguments")
    def _register_view(func):
        for arg in args:
            __registered_views.setdefault(root_tag_name, dict())[arg] = func
        return func
    return _register_view

__registered_views = {}

def __register_installed_applets():
    from django.conf import settings
    for applet in settings.DUCTUS_INSTALLED_APPLETS:
        try:
            __import__('%s.views' % applet, {}, {}, [''])
        except ImportError:
            raise "Could not import applet '%s'" % applet

__register_installed_applets()

@register_view(None, 'xml')
def view_xml(request, requested_view, urn, tree):
    """Displays XML representation of resource.
    """

    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='application/xml')

@register_view(None, 'xml_as_text')
def view_xml_as_text(request, requested_view, urn, tree):
    """Displays XML representation of resource in text/plain format.
    """

    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='text/plain')

try:
    import pygments, pygments.lexers, pygments.formatters
except ImportError:
    pass
else:
    @register_view(None, 'xml_as_html')
    def view_xml_as_html(request, requested_view, urn, tree):
        """Displays HTML-formatted XML representation of resource.
        """

        xml = ''.join(get_resource_database().get_xml(urn))

        lexer = pygments.lexers.XmlLexer()
        formatter = pygments.formatters.HtmlFormatter()
        html = urn_linkify(pygments.highlight(xml, lexer, formatter))
        css = formatter.get_style_defs('.highlight')

        return render_to_response('urn_xml.html',
                                  {'html': mark_safe(html),
                                   'css': mark_safe(css)},
                                  context_instance=RequestContext(request))

@register_view(None, 'view_index')
def view_view_index(request, requested_view, urn, tree):
    """Display the index of available views for the resource.
    """

    root_tag_name = tree.getroot().tag

    def get_views(tag):
        return __registered_views.get(tag, ())

    special_views = sorted(get_views(root_tag_name))
    generic_views = sorted(set(get_views(None)) - set(special_views))

    return render_to_response('urn_view_index.html',
                              {'special_views': special_views,
                               'generic_views': generic_views},
                              context_instance=RequestContext(request))
