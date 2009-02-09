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

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotModified, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.vary import vary_on_headers
from django.utils.safestring import mark_safe
from django.utils.cache import patch_vary_headers, patch_cache_control

from ductus.resource import determine_header
from ductus.wiki import get_resource_database, registered_views, registered_creation_views, SuccessfulEditRedirect, resolve_urn
from ductus.wiki.models import WikiPage, WikiRevision
from ductus.wiki.decorators import register_view, unvarying
from ductus.util.http import query_string_not_found

class DuctusRequestInfo(object):
    def __init__(self, resource, requested_view, wikipage):
        self.resource = resource
        self.requested_view = requested_view
        self.wikipage = wikipage

class __Http304(Exception):
    pass

def __handle_etag(request, key):
    from django.utils.hashcompat import md5_constructor
    etag = '"%s"' % md5_constructor(repr(key)).hexdigest()
    if etag == request.META.get('HTTP_IF_NONE_MATCH', None):
        raise __Http304
    return etag
    # fixme: we may also want to set last-modified, expires, max-age

def __catch_http304(func):
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except __Http304:
            return HttpResponseNotModified()
    return new_func

@__catch_http304
@vary_on_headers('Cookie', 'Accept-language')
def view_urn(request, hash_type, hash_digest, wikipage=False):
    """Dispatches the appropriate view for a resource
    """

    urn = 'urn:%s:%s' % (hash_type, hash_digest)
    requested_view = request.GET.get('view', None)

    if requested_view == 'raw':
        etag = __handle_etag(request, ['raw', urn])
        # fixme: we may also want to set last-modified, expires, max-age

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
        etag = __handle_etag(request, ['blob', urn])
        header, data_iterator = determine_header(data_iterator, False)
        response = HttpResponse(list(data_iterator), # see django #6527
                                content_type='application/octet-stream')
        response["Etag"] = etag
        return response

    if header == 'xml':
        del data_iterator

        etag = None
        if request.method == "GET":
            unvaried_etag = [urn, wikipage, request.META.get("QUERY_STRING", "")]
            varied_etag = unvaried_etag + [request.LANGUAGE_CODE,
                                           request.META.get("HTTP_COOKIE", "")]
            unvaried_etag = __handle_etag(request, unvaried_etag)
            varied_etag = __handle_etag(request, varied_etag)

        resource = resource_database.get_resource_object(urn)
        try:
            f = registered_views[resource.fqn][requested_view]
        except KeyError:
            try:
                f = registered_views[None][requested_view]
            except KeyError:
                return query_string_not_found(request)

        request.ductus = DuctusRequestInfo(resource, requested_view, wikipage)
        response = f(request)

        if request.method == "GET" and not response.has_header("ETag"):
            if getattr(response, "_unvarying", False):
                response["ETag"] = unvaried_etag
            else:
                vary_headers = set([h.strip().lower() for h in response.get("Vary", "").split(',') if h])
                if vary_headers.issubset(set(['cookie', 'accept-language'])):
                    response["ETag"] = varied_etag
        return response

    raise Http404

def _handle_successful_edit(request, response, page):
    # the underlying page has been modified, so we should take note of that
    # and save its new location
    revision = WikiRevision(page=page, urn=response.urn[4:])
    if request.user.is_authenticated():
        revision.author = request.user
    else:
        revision.author_ip = request.remote_addr
    revision.save()

def view_wikipage(request, pagename):
    try:
        page = WikiPage.objects.get(name=pagename)
    except WikiPage.DoesNotExist:
        return implicit_new_wikipage(request, pagename)

    if request.GET.get('view', None) in ('location_history', 'hybrid_history'):
        response = render_to_response('wiki/location_history.html',
                                      {'page': page},
                                      context_instance=RequestContext(request))
        patch_vary_headers(response, ['Cookie', 'Accept-language'])
        return response

    revision = page.get_latest_revision()
    if not revision.urn:
        return implicit_new_wikipage(request, pagename)

    hash_type, hash_digest = revision.urn.split(':')

    response = view_urn(request, hash_type, hash_digest, wikipage=True)

    if isinstance(response, SuccessfulEditRedirect):
        _handle_successful_edit(request, response, page)
        return HttpResponseRedirect(request.path)

    patch_cache_control(response, must_revalidate=True)
    return response

def implicit_new_wikipage(request, pagename):
    # fixme: should we just 404 if non-empty query_string?
    get_resource_database() # FIXME: we are only calling this because it registers all applets!
    return render_to_response('wiki/implicit_new_wikipage.html', {
        'pagename': pagename,
        'creation_views': registered_creation_views.keys(),
    }, context_instance=RequestContext(request))

def creation_view(request, page_type):
    get_resource_database() # FIXME: we are only calling this because it registers all applets!
    try:
        view_func = registered_creation_views[page_type]
    except KeyError:
        return HttpResponse(["Creation views for %s" % list(registered_creation_views)])
        raise Http404

    response = view_func(request)
    if "target" in request.GET and isinstance(response, SuccessfulEditRedirect):
        page, page_created = WikiPage.objects.get_or_create(name=request.GET["target"])
        if page_created:
            page.save()
        _handle_successful_edit(request, response, page)
        return HttpResponseRedirect(page.get_absolute_url())
    return response

@register_view(None, 'xml')
@unvarying
def view_xml(request):
    """Displays XML representation of resource.
    """

    urn = request.ductus.resource.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='application/xml')

@register_view(None, 'xml_as_text')
@unvarying
def view_xml_as_text(request):
    """Displays XML representation of resource in text/plain format.
    """

    urn = request.ductus.resource.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='text/plain')

def urn_linkify(html):
    """linkifies URNs

    This function assumes no URNs occur inside HTML tags, as it will attempt to
    linkify them anyway.
    """

    def repl(matchobj):
        urn = matchobj.group(0)
        return u'<a href="%s">%s</a>' % (resolve_urn(urn), urn)

    import re
    return re.sub(r'urn:[_\-A-Za-z0-9\:]*', repl, html)

try:
    import pygments, pygments.lexers, pygments.formatters
except ImportError:
    pass
else:
    @register_view(None, 'xml_as_html')
    def view_xml_as_html(request):
        """Displays HTML-formatted XML representation of resource.
        """

        urn = request.ductus.resource.urn
        xml = ''.join(get_resource_database().get_xml(urn))

        lexer = pygments.lexers.XmlLexer()
        formatter = pygments.formatters.HtmlFormatter()
        html = urn_linkify(pygments.highlight(xml, lexer, formatter))
        css = formatter.get_style_defs('.highlight')

        return render_to_response('wiki/xml_display.html',
                                  {'html': mark_safe(html),
                                   'css': mark_safe(css)},
                                  context_instance=RequestContext(request))

@register_view(None, 'view_index')
def view_view_index(request):
    """Display the index of available views for the resource.
    """

    root_tag_name = request.ductus.resource.fqn

    def get_views(tag):
        return registered_views.get(tag, ())

    special_views = sorted(get_views(root_tag_name))
    generic_views = sorted(set(get_views(None)) - set(special_views))

    return render_to_response('wiki/view_index.html',
                              {'special_views': special_views,
                               'generic_views': generic_views},
                              context_instance=RequestContext(request))

@register_view(None, 'document_history')
def view_document_history(request):
    return render_to_response('wiki/document_history.html',
                              context_instance=RequestContext(request))

@register_view(None, 'license_info')
def view_license_info(request):
    return render_to_response('wiki/license_info.html',
                              context_instance=RequestContext(request))
