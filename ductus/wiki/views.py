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

import json
import re
import logging
from urllib2 import urlopen, HTTPError as urllib2_HTTPError

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotModified, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader
from django.views.decorators.vary import vary_on_headers
from django.utils.safestring import mark_safe
from django.utils.cache import patch_cache_control, patch_response_headers
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy, ugettext as _
from django.conf import settings

from ductus.resource import get_resource_database, determine_header
from ductus.resource.ductmodels import DuctModel
from ductus.wiki import registered_views, registered_creation_views, SuccessfulEditRedirect, resolve_urn, is_legal_wiki_pagename, user_has_edit_permission, user_has_unlink_permission
from ductus.wiki.namespaces import BaseWikiNamespace, registered_namespaces, split_pagename, join_pagename, WikiPrefixNotProvided
from ductus.wiki.models import WikiPage, WikiRevision
from ductus.wiki.decorators import register_view
from ductus.wiki.subviews import subview
from ductus.decorators import unvarying
from ductus.util.http import query_string_not_found, render_json_response, ImmediateResponse

logger = logging.getLogger(__name__)

# The following can be removed once we upgrade to Django 1.5, as it will
# supposedly do a strict check to make sure SECRET_KEY is not blank.
if not settings.SECRET_KEY:
    raise Exception("You must define a SECRET_KEY in ductus_local_settings.py.")

def view_frontpage(request):
    "Use the custom 'otics' front page, or redirect based on the user's locale"
    if 'ductus.modules.otics' in settings.DUCTUS_INSTALLED_MODULES:
        from ductus.modules.otics.views import otics_front_page
        return otics_front_page(request)
    return redirect('/%s' % _('en:main_page').replace(':', '/', 1))

class DuctusRequestInfo(object):
    def __init__(self, resource, requested_view, wiki_page, wiki_revision):
        self.resource = resource
        self.requested_view = requested_view
        self.wiki_page = wiki_page
        self.wiki_revision = wiki_revision

def __handle_etag(request, key, weak=True):
    from django.utils.hashcompat import md5_constructor
    etag = '"%s"' % md5_constructor(repr(key)).hexdigest()
    if weak: # use a "weak entity tag" since byte equality is not guaranteed
        etag = 'W/' + etag
    if etag == request.META.get('HTTP_IF_NONE_MATCH', None):
        raise ImmediateResponse(HttpResponseNotModified())
    return etag

@vary_on_headers('Cookie', 'Accept-language')
def main_document_view(request, urn=None, wiki_page=None, wiki_revision=None):
    """Dispatches the appropriate view for a resource/page
    """

    requested_view = request.GET.get('view', None)

    if requested_view == 'raw':
        etag = __handle_etag(request, ['raw', urn], weak=False)
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
        etag = __handle_etag(request, ['blob', urn], weak=False)
        header, data_iterator = determine_header(data_iterator, False)
        response = HttpResponse(list(data_iterator), # see django #6527
                                content_type='application/octet-stream')
        response["ETag"] = etag
        return response

    if header == 'xml':
        del data_iterator

        etag = None
        if request.method == "GET":
            unvaried_etag = [urn, bool(wiki_page),
                             request.META.get("QUERY_STRING", "")]
            varied_etag = unvaried_etag + [request.LANGUAGE_CODE,
                                           bool(request.is_secure()),
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
    return main_document_view(request, urn)

def check_edit_permission(request, prefix, pagename, status=403):
    if not user_has_edit_permission(request.user, prefix, pagename):
        t = loader.get_template('wiki/no_edit_permission.html')
        raise ImmediateResponse(t.render(RequestContext(request)),
                                status=status)

def check_create_permission(request, prefix, pagename, status=404):
    if not user_has_edit_permission(request.user, prefix, pagename):
        t = loader.get_template('wiki/no_create_permission.html')
        raise ImmediateResponse(t.render(RequestContext(request)),
                                status=status)

def check_unlink_permission(request, prefix, pagename, status=403):
    if not user_has_unlink_permission(request.user, prefix, pagename):
        t = loader.get_template('wiki/no_unlink_permission.html')
        raise ImmediateResponse(t.render(RequestContext(request)),
                                status=status)

def construct_wiki_revision(page, urn, request):
    # the 'urn:' should already be chopped off
    assert not urn.startswith('urn:')

    # we shouldn't be preparing to modify server state on a GET request
    assert request.method != 'GET'

    revision = WikiRevision(page=page, urn=urn)
    if request.user.is_authenticated():
        revision.author = request.user
    else:
        revision.author_ip = request.remote_addr
    revision.log_message = request.POST.get("log_message", "")
    return revision

def _handle_successful_wikiedit(request, response, page):
    # the underlying page has been modified, so we should take note of that
    # and save its new location

    if response.handled:
        return response
    response.handled = True

    check_edit_permission(request, *page.split_pagename())

    revision = construct_wiki_revision(page, response.urn[4:], request)
    revision.save()
    response.set_redirect_url(page.get_absolute_url())
    return response

def handle_blueprint_post(request, expected_model=DuctModel):
    # this is not a view, but rather a function that is meant to be called by
    # views.  should be put such functions somewhere else?
    from functools import partial
    from django.http import HttpResponseBadRequest
    HttpTextResponseBadRequest = partial(HttpResponseBadRequest,
                                         content_type="text/plain; charset=utf-8")

    from ductus.resource.ductmodels import BlueprintSaveContext, BlueprintError, ValidationError

    try:
        blueprint = json.loads(request.POST['blueprint'])
    except KeyError:
        return HttpTextResponseBadRequest(u"no blueprint given")
    except ValueError:
        return HttpTextResponseBadRequest(u"json fails to parse")
    save_context = BlueprintSaveContext.from_request(request)
    try:
        urn = expected_model.save_blueprint(blueprint, save_context)
    except BlueprintError, e:
        return HttpTextResponseBadRequest(str(e))
    except ValidationError, e:
        logger.debug("validation failed: %s", e)
        if settings.DEBUG:
            import sys
            import traceback
            exc_type, exc_info, tb = sys.exc_info()
            msg = list(traceback.format_tb(tb))
            msg.append(exc_type.__name__)
            msg.append(repr(exc_info))
            logger.error("\n".join(msg))
        return HttpTextResponseBadRequest(u"validation failed")
    return SuccessfulEditRedirect(urn)

def _fully_handle_blueprint_post(request, prefix, pagename):
    if not is_legal_wiki_pagename(prefix, pagename):
        raise Http404
    check_edit_permission(request, prefix, pagename)

    response = handle_blueprint_post(request)

    if isinstance(response, SuccessfulEditRedirect):
        page, page_created = WikiPage.objects.get_or_create(name=join_pagename(prefix, pagename))
        return _handle_successful_wikiedit(request, response, page)

    return response

def view_wikipage(request, prefix, pagename):
    """Used for pages represented by a WikiPage"""

    if not is_legal_wiki_pagename(prefix, pagename):
        raise Http404

    if request.method == 'POST' and not request.GET.get('view', None):
        return _fully_handle_blueprint_post(request, prefix, pagename)

    name = join_pagename(prefix, pagename)
    try:
        page = WikiPage.objects.get(name=name)
    except WikiPage.DoesNotExist:
        page = None

    if page:
        if "oldid" in request.GET:
            try:
                revision = WikiRevision.objects.get(id=request.GET["oldid"], page=page)
            except (ValueError, WikiRevision.DoesNotExist):
                return query_string_not_found(request)
            if not revision.urn:
                return query_string_not_found(request)
        else:
            revision = page.get_latest_revision()
    else:
        revision = None

    if revision is None and getattr(settings, "DUCTUS_WIKI_REMOTE", None):
        # See if DUCTUS_WIKI_REMOTE has the page
        try:
            remote_url = "%s%s?view=urn" % (settings.DUCTUS_WIKI_REMOTE, iri_to_uri(urlquote(u'%s/%s' % (prefix, pagename))))
            remote_urn = json.loads(urlopen(remote_url).read(1000))["urn"]
            # we never actually save this WikiPage or WikiRevision to the database
            if page is None:
                page, page_created = WikiPage.objects.get_or_create(name=name)
            revision = WikiRevision(page=page, urn=remote_urn[4:])
        except urllib2_HTTPError:
            pass

    if revision and revision.urn:
        urn = 'urn:' + revision.urn
    else:
        urn = None

    if request.GET.get('view', None) == 'urn':
        if revision:
            return render_json_response({"urn": urn})

    response = None

    if urn:
        response = main_document_view(request, urn, page, revision)
        if isinstance(response, SuccessfulEditRedirect):
            return _handle_successful_wikiedit(request, response, page)
        response["X-Ductus-URN"] = urn
    else:
        requested_view = request.GET.get("view", None)
        request.ductus = DuctusRequestInfo(None, requested_view, page, revision)
        if requested_view:
            f = registered_views[None].get(requested_view, None)
            if f and f.meets_requirements(request.ductus):
                response = f(request)

    if response is None:
        response = implicit_new_wikipage(request, prefix, pagename)

    # wikipage urls expire immediately since they can frequently be edited
    patch_response_headers(response, cache_timeout=0)
    patch_cache_control(response, must_revalidate=True)

    return response

def _get_creation_views():
    order = dict([(x, i + 1) for i, x in enumerate(['wikitext', 'lesson', 'standalone-media'])])
    def sort_key(creation_view):
        given_order = order.get(creation_view.name, None) or order.get(creation_view.category, None) or (len(order) + 1)
        return (given_order, creation_view.name)
    creation_views = sorted(registered_creation_views.values(), key=sort_key)
    # work around not having `do_not_call_in_templates` in django < 1.4
    creation_views = [{'name': v.name, 'description': v.description}
                      for v in creation_views]
    return creation_views

def _get_creation_templates():
    # put together a list of wiki content templates for the /new page
    rv = []
    rv.append({ 'class': 'wikitext',
                'name': _('Wikitext'),
                'url': '/new/wikitext',
                'description': _('a regular wiki text page')})
    rv.append({ 'class': 'podcast',
                'name': _('Podcast'),
                'url': '/new/flashcard_deck?template=podcast',
                'description': _('a lesson that compiles into a downloadable podcast')})
    rv.append({ 'class': 'picture_choice',
                'name': _('Picture choice'),
                'url': '/new/flashcard_deck?template=picture_choice',
                'description': _('a lesson where you choose between multiple pictures')})
    rv.append({ 'class': 'phrase_choice',
                'name': _('Phrase choice'),
                'url': '/new/flashcard_deck?template=phrase_choice',
                'description': _('a lesson where you choose between multiple phrases')})
    return rv

def implicit_new_wikipage(request, prefix, pagename):
    c = RequestContext(request, {
        'absolute_pagename': join_pagename(prefix, pagename),
        'advanced_view': 'advanced' in request.GET,
        'creation_templates': _get_creation_templates(),
        'creation_views': _get_creation_views(),
    })
    check_create_permission(request, prefix, pagename)
    t = loader.get_template('wiki/new_wikipage.html')
    return HttpResponse(t.render(c), status=404)

def explicit_new_wikipage(request):
    return render_to_response('wiki/new_wikipage.html', {
        'advanced_view': 'advanced' in request.GET,
        'creation_templates': _get_creation_templates(),
        'creation_views': _get_creation_views(),
    }, RequestContext(request))

def creation_view(request, page_type):
    try:
        view_func = registered_creation_views[page_type]
    except KeyError:
        raise Http404

    response = view_func(request)
    if "target" in request.GET:
        try:
            target = split_pagename(request.GET["target"])
        except WikiPrefixNotProvided:
            raise Http404
        if not is_legal_wiki_pagename(*target):
            raise Http404
        check_edit_permission(request, *target)
    if "target" in request.GET and isinstance(response, SuccessfulEditRedirect):
        page, page_created = WikiPage.objects.get_or_create(name=join_pagename(*target))
        return _handle_successful_wikiedit(request, response, page)
    return response

def wiki_dispatch(request, prefix, pagename):
    try:
        wns = registered_namespaces[prefix]
    except KeyError:
        raise Http404("prefix not registered")

    request.ductus_prefix = prefix

    return wns.view_page(request, pagename)

class RegularWikiNamespace(BaseWikiNamespace):
    allow_page_creation = True

    def page_exists(self, pagename):
        from ductus.wiki.models import WikiPage
        name = join_pagename(self.prefix, pagename)
        try:
            latest = WikiPage.objects.get(name=name).get_latest_revision()
            if latest and latest.urn:
                return True
        except WikiPage.DoesNotExist:
            pass

        return False

    def allow_edit(self, user, pagename):
        return True

    def view_page(self, request, pagename):
        return view_wikipage(request, self.prefix, pagename)

class NaturalLanguageWikiNamespace(RegularWikiNamespace):
    pass

for __language in settings.DUCTUS_NATURAL_LANGUAGES:
    NaturalLanguageWikiNamespace(__language)

class UrnWikiNamespace(BaseWikiNamespace):
    __urn_slash_re = re.compile(r'(?P<hash_type>[-_\w]+)/(?P<digest>[-_\w]+)')
    __urn_colon_re = re.compile(r'(?P<hash_type>[-_\w]+):(?P<digest>[-_\w]+)')

    def page_exists(self, pagename):
        match = self.__urn_colon_re.match(pagename)
        if not match:
            return False
        hash_type, hash_digest = match.group(1), match.group(2)

        resource_database = get_resource_database()
        urn = 'urn:%s:%s' % (hash_type, hash_digest)
        # this will return True for blobs as well.  do we really want this?
        return urn in resource_database

    def path_func(self, pagename):
        return pagename.replace(':', '/', 1)

    def view_page(self, request, pagename):
        match = self.__urn_slash_re.match(pagename)
        if not match:
            raise Http404('invalid format for urn')
        hash_type, hash_digest = match.group(1), match.group(2)
        return view_urn(request, hash_type, hash_digest)

UrnWikiNamespace('urn')

class NewPageNamespace(BaseWikiNamespace):
    def __init__(self):
        super(NewPageNamespace, self).__init__('new')

    def page_exists(self, pagename):
        return bool(pagename in registered_creation_views)

    def view_page(self, request, pagename):
        return creation_view(request, pagename)

NewPageNamespace()

@register_view(None, 'copy')
def view_copy_resource(request):
    """Copies/forks the resource to a new location on the wiki
    """

    from django import forms

    class CopyPageForm(forms.Form):
        source_urn = forms.CharField(widget=forms.HiddenInput())
        target_pagename = forms.CharField(label=_('Target page name'), help_text=_('wiki location of the new resource'))

        def clean_source_urn(self):
            source_urn = self.cleaned_data['source_urn']
            try:
                source_resource = get_resource_database().get_resource_object(source_urn)
            except Exception: # fixme: some day we should just be able to catch KeyError here, or something
                raise forms.ValidationError(_('source resource does not exist'))
            else:
                return source_urn

        def clean_target_pagename(self):
            target_pagename = self.cleaned_data['target_pagename']

            # convert spaces to underscores
            r = re.compile(r'[\s_]+', re.UNICODE)
            target_pagename = r.sub(u'_', target_pagename)
            # remove leading and trailing underscores from each portion of
            # path; remove extra slashes
            target_pagename = u'/'.join(filter(lambda x: x, [a.strip(u'_') for a in target_pagename.split(u'/')]))

            # deal with namespace
            prefix, pagename = split_pagename(target_pagename, fallback_prefix=request.ductus_prefix)
            target_pagename = join_pagename(prefix, pagename)

            # make sure we can create the page
            if not is_legal_wiki_pagename(prefix, pagename):
                raise forms.ValidationError(_(u'Invalid page name')) # would be nice to tell the user why it's invalid...
            if not user_has_edit_permission(request.user, prefix, pagename):
                raise forms.ValidationError(_('you do not have permission to create/write to this resource'))
            return target_pagename

    if request.method == 'POST':
        form = CopyPageForm(request.POST)
        if form.is_valid():
            source_urn = form.cleaned_data['source_urn']
            source_resource = get_resource_database().get_resource_object(source_urn)
            target_pagename = form.cleaned_data['target_pagename']
            page, page_created = WikiPage.objects.get_or_create(name=target_pagename)
            response = SuccessfulEditRedirect(source_urn)
            return _handle_successful_wikiedit(request, response, page)
    else:
        form = CopyPageForm(initial={'source_urn': request.ductus.resource.urn})

    return render_to_response('wiki/copy.html', {
        'form': form,
    }, RequestContext(request))

if settings.DEBUG:
    @register_view(None, 'DEBUG_json')
    def view_json(request):
        urn = request.ductus.resource.urn
        resource = get_resource_database().get_resource_object(urn)
        json_text = json.dumps(resource.output_json_dict())
        return HttpResponse(json_text, content_type='text/plain; charset=utf-8')

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

def urn_linkify(html, query_string=''):
    """linkifies URNs

    This function assumes no URNs occur inside HTML tags, as it will attempt to
    linkify them anyway.
    """

    if query_string:
        query_string = '?' + query_string

    def repl(matchobj):
        urn = matchobj.group(0)
        return u'<a href="%s">%s</a>' % (resolve_urn(urn) + query_string, urn)

    return re.sub(r'urn:[_\-A-Za-z0-9\:]*', repl, html)

def allow_line_wrap(html):
    return html.replace('pre>', 'code>').replace('\n', '<br/>\n')

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
        html = allow_line_wrap(pygments.highlight(xml, lexer, formatter))
        html = urn_linkify(html, query_string='view=xml_as_html')
        css = formatter.get_style_defs('.highlight')

        return render_to_response('wiki/xml_display.html',
                                  {'html': mark_safe(html),
                                   'css': mark_safe(css)},
                                  context_instance=RequestContext(request))

@register_view(None, 'view_index', requires=None)
def view_view_index(request):
    """Display the index of available views for the resource/page.
    """

    def get_views(tag):
        rv = [label for label, view in registered_views.get(tag, ()).items()
              if view.meets_requirements(request.ductus)]
        if "show_all" not in request.GET:
            rv = [lbl for lbl in rv if lbl is None or not lbl.startswith('_')]
        return rv

    if request.ductus.resource:
        special_views = sorted(get_views(request.ductus.resource.fqn))
    else:
        special_views = []
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
def view_location_history(request):
    return render_to_response('wiki/location_history.html',
                              context_instance=RequestContext(request))

@register_view(None, 'history', requires=lambda d: d.wiki_page or d.resource)
def view_history(request):
    if request.ductus.wiki_page:
        return view_location_history(request)
    else:
        return view_document_history(request)

@register_view(None, 'unlink', requires=lambda d: d.wiki_revision)
def view_unlink_wikipage(request):
    check_unlink_permission(request, *request.ductus.wiki_page.split_pagename())

    if request.ductus.wiki_revision.urn == "":
        return render_to_response('wiki/unlink_deleted.html', {
            'already_deleted': True,
        }, RequestContext(request))

    if request.method == 'POST':
        revision = construct_wiki_revision(request.ductus.wiki_page, "", request)
        revision.save()
        return render_to_response('wiki/unlink_deleted.html', {
        }, RequestContext(request))

    return render_to_response('wiki/unlink_confirm.html', {
    }, RequestContext(request))

@register_view(None, 'license_info')
def view_license_info(request):
    resource_database = get_resource_database()

    resource = request.ductus.resource
    resources = [resource]
    resources.extend(resource_database.get_resource_object(urn)
                     for urn in subview(resource).subresources())

    return render_to_response('wiki/all_license_info.html', {
        'resources': resources,
    }, context_instance=RequestContext(request))

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
        from ductus.resource.ductmodels import TextElement, ArrayElement

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
        # resource object doesn't exist.  Let's first try to diff against one
        # of the parents, and fail out if that doesn't work.
        if this.common.parents.array:
            that = this.common.parents.array[0].get()
        else:
            return query_string_not_found(request)

    return render_to_response("wiki/diff.html", {
        'diff': Diff(this, that),
    }, RequestContext(request))
