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

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django import forms

from ductus.resource import get_resource_database
from ductus.wiki.decorators import register_view, register_creation_view
from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.namespaces import registered_namespaces, split_pagename, WikiPrefixNotProvided
from ductus.wiki.forms import LogMessageField
from ductus.modules.textwiki.ductmodels import Wikitext
from ductus.util.bcp47 import language_tag_to_description

recaptcha = None
if hasattr(settings, "RECAPTCHA_PRIVATE_KEY"):
    from recaptcha.client import captcha as recaptcha

# fixme: in this default view, lower the cache time for when links change from
# broken to unbroken and back
@register_view(Wikitext)
def view_textwiki(request):
    return render_to_response('textwiki/display_wiki.html', {
        'text': request.ductus.resource.text,
        'natural_language': request.ductus.resource.blob.natural_language or None,
    }, context_instance=RequestContext(request))

_natural_language_choices = [('', ugettext_lazy('Unspecified'))]
_natural_language_choices.extend((code, ugettext_lazy(language_tag_to_description(code)))
                                 for code in settings.DUCTUS_NATURAL_LANGUAGES)

class WikiEditForm(forms.Form):
    textarea_attrs = {'cols': '80', 'rows': '30'}
    text = forms.CharField(widget=forms.Textarea(attrs=textarea_attrs))
    natural_language = forms.ChoiceField(required=False, choices=_natural_language_choices)
    log_message = LogMessageField()

def add_author_and_log_message(request, resource):
    if request.user.is_authenticated():
        resource.common.author.text = request.user.username
        if getattr(settings, "DUCTUS_SITE_DOMAIN", None):
            resource.common.author.href = 'http://%s%s' % (settings.DUCTUS_SITE_DOMAIN, request.user.get_absolute_url())
    else:
        resource.common.author.text = request.remote_addr
    resource.common.log_message.text = request.POST.get('log_message', '')

@register_creation_view(Wikitext, description=ugettext_lazy('a "regular" text-based wiki page, using wiki-creole as markup'))
@register_view(Wikitext, 'edit')
def edit_textwiki(request):
    resource_database = get_resource_database()
    if "parent" in request.POST:
        # fixme: this could raise exceptions if not found
        resource = resource_database.get_resource_object(request.POST["parent"])
        if not isinstance(resource, Wikitext):
            raise Exception
    elif hasattr(request, 'ductus'):
        resource = request.ductus.resource
    else:
        resource = None

    preview_requested = ('preview' in request.POST)

    if request.method == 'POST':
        if recaptcha is not None and not request.user.is_authenticated():
            if not ('recaptcha_challenge_field' in request.POST
                    and 'recaptcha_response_field' in request.POST
                    and recaptcha.submit(request.POST['recaptcha_challenge_field'],
                                         request.POST['recaptcha_response_field'],
                                         settings.RECAPTCHA_PRIVATE_KEY,
                                         request.remote_addr).is_valid):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("invalid captcha")

        form = WikiEditForm(request.POST)

        if form.is_valid() and not preview_requested:
            if form.cleaned_data['text'].strip() == '':
                raise Exception
            if resource:
                resource = resource.clone()
            else:
                resource = Wikitext()
            resource.text = form.cleaned_data['text'].replace('\r', '')
            resource.blob.natural_language = form.cleaned_data['natural_language']
            add_author_and_log_message(request, resource)
            urn = resource.save()
            return SuccessfulEditRedirect(urn)

    else:
        if resource:
            form = WikiEditForm(initial={
                'text': resource.text,
                'natural_language': resource.blob.natural_language or '',
            })
        else:
            # blank form, but try to guess the natural language
            try:
                prefix, pagename = split_pagename(request.GET.get('target', ''))
            except WikiPrefixNotProvided:
                prefix = None
            if (prefix and
                    prefix in [p for p, n in _natural_language_choices] and
                    prefix in registered_namespaces):
                form = WikiEditForm(initial={'natural_language': prefix})
            else:
                form = WikiEditForm()

    captcha_html = ""
    if recaptcha is not None and not request.user.is_authenticated():
        captcha_html = recaptcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY,
                                             use_ssl=request.is_secure())
        captcha_html = captcha_html.replace('frameborder="0"',
                                            'style="border: 0"')

    return render_to_response('textwiki/edit_wiki.html', {
        'form': form,
        'parent_urn': (resource and resource.urn),
        'captcha': mark_safe(captcha_html),
        'show_preview': (preview_requested and form.is_valid()),
    }, context_instance=RequestContext(request))

new_textwiki = edit_textwiki
