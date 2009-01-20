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
from django.views.decorators.vary import vary_on_headers
from django.utils.safestring import mark_safe

from ductus.resource import determine_header
from ductus.urn import get_resource_database
from ductus.urn.util import urn_linkify
from ductus.util.http import query_string_not_found, Http304

class DuctusRequestInfo(object):
    def __init__(self, urn, requested_view, xml_tree):
        self.urn = urn
        self.requested_view = requested_view
        self.xml_tree = xml_tree

def handle_etag(request, key):
    from django.utils.hashcompat import md5_constructor
    etag = '"%s"' % md5_constructor(repr(key)).hexdigest()
    if etag == request.META.get('HTTP_IF_NONE_MATCH', None):
        raise Http304
    return etag
    # fixme: we may also want to set last-modified and expires headers

def view_urn(request, hash_type, hash_digest):
    """Dispatches the appropriate view for a resource
    """

    urn = 'urn:%s:%s' % (hash_type, hash_digest)
    requested_view = request.GET.get('view', None)

    if requested_view == 'raw':
        etag = handle_etag(request, ['raw', urn])
        # fixme: we may also want to set last-modified and expires headers

    resource_database = get_resource_database()
    try:
        data_iterator = resource_database[urn]
    except KeyError:
        raise Http404
    header, data_iterator = determine_header(data_iterator)

    if requested_view == 'raw':
        response = HttpResponse(list(data_iterator), # see django #6527
                                content_type='application/octet-stream')
        response["ETag"] = etag
        return response

    if header == 'blob':
        etag = handle_etag(request, ['blob', urn])
        header, data_iterator = determine_header(data_iterator, False)
        response = HttpResponse(list(data_iterator), # see django #6527
                                content_type='application/octet-stream')
        response["Etag"] = etag
        return response

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
                return query_string_not_found(request)

        request.ductus = DuctusRequestInfo(urn, requested_view, tree)
        return f(request)

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

@register_view(None, 'xml')
def view_xml(request):
    """Displays XML representation of resource.
    """

    urn = request.ductus.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='application/xml')

@register_view(None, 'xml_as_text')
def view_xml_as_text(request):
    """Displays XML representation of resource in text/plain format.
    """

    urn = request.ductus.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='text/plain')

try:
    import pygments, pygments.lexers, pygments.formatters
except ImportError:
    pass
else:
    @register_view(None, 'xml_as_html')
    @vary_on_headers('Cookie', 'Accept-language')
    def view_xml_as_html(request):
        """Displays HTML-formatted XML representation of resource.
        """

        xml = ''.join(get_resource_database().get_xml(request.ductus.urn))

        lexer = pygments.lexers.XmlLexer()
        formatter = pygments.formatters.HtmlFormatter()
        html = urn_linkify(pygments.highlight(xml, lexer, formatter))
        css = formatter.get_style_defs('.highlight')

        return render_to_response('urn/xml_display.html',
                                  {'html': mark_safe(html),
                                   'css': mark_safe(css)},
                                  context_instance=RequestContext(request))

@register_view(None, 'view_index')
@vary_on_headers('Cookie', 'Accept-language')
def view_view_index(request):
    """Display the index of available views for the resource.
    """

    root_tag_name = request.ductus.xml_tree.getroot().tag

    def get_views(tag):
        return __registered_views.get(tag, ())

    special_views = sorted(get_views(root_tag_name))
    generic_views = sorted(set(get_views(None)) - set(special_views))

    return render_to_response('urn/view_index.html',
                              {'special_views': special_views,
                               'generic_views': generic_views},
                              context_instance=RequestContext(request))
