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

try:
    import json
except ImportError:
    from django.utils import simplejson as json
from urllib2 import urlopen, HTTPError as urllib2_HTTPError

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotModified, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.decorators.vary import vary_on_headers
from django.utils.safestring import mark_safe
from django.utils.cache import patch_cache_control
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.conf import settings

from ductus.resource import determine_header
from ductus.wiki import get_resource_database, registered_views, registered_creation_views, SuccessfulEditRedirect, resolve_urn
from ductus.wiki.models import WikiPage, WikiRevision
from ductus.wiki.decorators import register_view, unvarying
from ductus.util.http import query_string_not_found, render_json_response

class DuctusRequestInfo(object):
    def __init__(self, resource, requested_view, wiki_page, wiki_revision):
        self.resource = resource
        self.requested_view = requested_view
        self.wiki_page = wiki_page
        self.wiki_revision = wiki_revision

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
def main_view(request, urn=None, wiki_page=None, wiki_revision=None):
    """Dispatches the appropriate view for a resource/page
    """

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
            unvaried_etag = [urn, bool(wiki_page),
                             request.META.get("QUERY_STRING", "")]
            varied_etag = unvaried_etag + [request.LANGUAGE_CODE,
                                           request.META.get("HTTP_COOKIE", "")]
            unvaried_etag = __handle_etag(request, unvaried_etag)
            varied_etag = __handle_etag(request, varied_etag)

        resource = resource_database.get_resource_object(urn)
        request.ductus = DuctusRequestInfo(resource, requested_view,
                                           wiki_page, wiki_revision)

        try:
            f = registered_views[resource.fqn][requested_view]
        except KeyError:
            try:
                f = registered_views[None][requested_view]
            except KeyError:
                return query_string_not_found(request)
        if not f.meets_requirements(request.ductus):
            return query_string_not_found(request)
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

def view_urn(request, hash_type, hash_digest):
    urn = 'urn:%s:%s' % (hash_type, hash_digest)
    return main_view(request, urn)

def _handle_successful_wikiedit(request, response, page):
    # the underlying page has been modified, so we should take note of that
    # and save its new location

    # fixme: check for permission

    revision = WikiRevision(page=page, urn=response.urn[4:])
    if request.user.is_authenticated():
        revision.author = request.user
    else:
        revision.author_ip = request.remote_addr
    revision.log_message = request.POST.get("log_message", "")
    revision.save()
    response.set_redirect_url(page.get_absolute_url())
    return response

def view_wikipage(request, pagename):
    try:
        page = WikiPage.objects.get(name=pagename)
    except WikiPage.DoesNotExist:
        page = None

    if page:
        if "oldid" in request.GET:
            revision = get_object_or_404(WikiRevision, pk=request.GET["oldid"], page=page)
        else:
            revision = page.get_latest_revision()
    else:
        revision = None

    if revision is None and getattr(settings, "DUCTUS_WIKI_REMOTE", None):
        # See if DUCTUS_WIKI_REMOTE has the page
        try:
            remote_url = "%s/%s?view=urn" % (settings.DUCTUS_WIKI_REMOTE, iri_to_uri(urlquote(pagename)))
            remote_urn = json.loads(urlopen(remote_url).read(1000))["urn"]
            # we never actually save this WikiPage or WikiRevision to the database
            if page is None:
                page, page_created = WikiPage.objects.get_or_create(name=pagename)
                if page_created:
                    page.save()
            revision = WikiRevision(page=page, urn=remote_urn[4:])
        except urllib2_HTTPError:
            pass

    if request.GET.get('view', None) == 'urn':
        # fixme: we should just have an X-Urn header and use HEAD instead of GET
        if revision:
            return render_json_response({"urn": "urn:" + revision.urn})

    if revision:
        response = main_view(request, ("urn:" + revision.urn), page, revision)
        if isinstance(response, SuccessfulEditRedirect):
            return _handle_successful_wikiedit(request, response, page)
    else:
        response = implicit_new_wikipage(request, pagename)

    patch_cache_control(response, must_revalidate=True)
    return response

def implicit_new_wikipage(request, pagename):
    c = RequestContext(request, {
        'pagename': pagename,
        'creation_views': registered_creation_views.keys(),
    })
    t = loader.get_template('wiki/implicit_new_wikipage.html')
    return HttpResponse(t.render(c), status=404)

def creation_view(request, page_type):
    try:
        view_func = registered_creation_views[page_type]
    except KeyError:
        raise Http404

    response = view_func(request)
    if "target" in request.GET and isinstance(response, SuccessfulEditRedirect):
        page, page_created = WikiPage.objects.get_or_create(name=request.GET["target"])
        if page_created:
            page.save()
        return _handle_successful_wikiedit(request, response, page)
    return response

@register_view(None, 'xml')
@unvarying
def view_xml(request):
    """Displays XML representation of resource.
    """

    urn = request.ductus.resource.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='application/xml; charset=utf-8')

@register_view(None, 'xml_as_text')
@unvarying
def view_xml_as_text(request):
    """Displays XML representation of resource in text/plain format.
    """

    urn = request.ductus.resource.urn
    return HttpResponse(list(get_resource_database().get_xml(urn)), # see django #6527
                        content_type='text/plain; charset=utf-8')

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

def allow_line_wrap(html):
    return html.replace('pre>', 'tt>').replace('\n', '<br/>\n')

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
        html = urn_linkify(allow_line_wrap(pygments.highlight(xml, lexer, formatter)))
        css = formatter.get_style_defs('.highlight')

        return render_to_response('wiki/xml_display.html',
                                  {'html': mark_safe(html),
                                   'css': mark_safe(css)},
                                  context_instance=RequestContext(request))

@register_view(None, 'view_index', requires=None)
def view_view_index(request):
    """Display the index of available views for the resource/page.
    """

    root_tag_name = request.ductus.resource.fqn

    def get_views(tag):
        rv = [label for label, view in registered_views.get(tag, ()).items()
              if view.meets_requirements(request.ductus)]
        if "show_all" not in request.GET:
            rv = [lbl for lbl in rv if lbl is None or not lbl.startswith('_')]
        return rv

    special_views = sorted(get_views(root_tag_name))
    generic_views = set(get_views(None)) - set(special_views)
    generic_views.discard("view_index") # no reason to list ourself
    generic_views = sorted(generic_views)

    return render_to_response('wiki/view_index.html',
                              {'special_views': special_views,
                               'generic_views': generic_views},
                              context_instance=RequestContext(request))

@register_view(None, 'document_history')
def view_document_history(request):
    return render_to_response('wiki/document_history.html',
                              context_instance=RequestContext(request))

@register_view(None, 'location_history', requires=lambda d: d.wiki_page)
@register_view(None, 'history', requires=lambda d: d.wiki_page)
def view_location_history(request):
    return render_to_response('wiki/location_history.html',
                              context_instance=RequestContext(request))

@register_view(None, 'license_info')
def view_license_info(request):
    return render_to_response('wiki/license_info.html',
                              context_instance=RequestContext(request))

class DiffItem(object):
    __slots__ = ('hierarchy', 'different', 'this', 'that')

    def __init__(self, hierarchy, different, this, that):
        self.hierarchy = hierarchy
        self.different = bool(different)
        self.this = unicode(this)
        self.that = unicode(that)

class Diff(list):
    def __init__(self, this, that):
        super(Diff, self).__init__()
        self.__do_diff(this, that)

    def __do_diff(self, this, that, hierarchy=()):
        from ductus.resource.models import TextElement, ArrayElement

        if type(this) is not type(that):
            self.append(DiffItem(hierarchy, True,
                                 "Type <%s>" % type(this),
                                 "Type <%s>" % type(that)))
            return

        elements_are_equal = (this == that)
        if hierarchy:
            label = "[%s]" % hierarchy[-1]
            self.append(DiffItem(hierarchy, not elements_are_equal,
                                 label, label))
        if elements_are_equal:
            return

        for attribute in this.attributes:
            this_attribute = getattr(this, attribute)
            that_attribute = getattr(that, attribute)
            self.append(DiffItem(hierarchy + (attribute,),
                                 (this_attribute != that_attribute),
                                 this_attribute, that_attribute))
        for subelement in this.subelements:
            self.__do_diff(getattr(this, subelement), getattr(that, subelement),
                           hierarchy + (subelement,))
        if isinstance(this, TextElement):
            self.append(DiffItem(hierarchy + ("text",),
                                 (this.text != that.text),
                                 this.text, that.text))
        if isinstance(this, ArrayElement):
            pass # fixme

@register_view(None, 'diff')
def view_diff(request):
    this = request.ductus.resource
    try:
        that = get_resource_database().get_resource_object(request.GET["diff"])
    except KeyError:
        # This could mean there is no "diff" in the query string, or that the
        # resource object doesn't exist.  Either way, we do the same thing.
        return query_string_not_found(request)

    return render_to_response("wiki/diff.html", {
        'diff': Diff(this, that),
    }, RequestContext(request))
