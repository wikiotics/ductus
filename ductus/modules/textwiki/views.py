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
from django import forms

from ductus.wiki.decorators import register_view, register_creation_view
from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.forms import LogMessageField
from ductus.modules.textwiki.models import Wikitext

recaptcha = None
if hasattr(settings, "RECAPTCHA_PRIVATE_KEY"):
    from recaptcha.client import captcha as recaptcha

# fixme: in this default view, lower the cache time for when links change from
# broken to unbroken and back
@register_view(Wikitext)
def view_textwiki(request):
    return render_to_response('textwiki/display_wiki.html',
                              {'text': request.ductus.resource.text},
                              context_instance=RequestContext(request))

class WikiEditForm(forms.Form):
    textarea_attrs = {'cols': '80', 'rows': '30'}
    text = forms.CharField(widget=forms.Textarea(attrs=textarea_attrs))
    log_message = LogMessageField()

def add_author_and_log_message(request, resource):
    if request.user.is_authenticated():
        resource.common.author.text = request.user.username
        #resource.common.author.href = "%s" % urlescape(request.user.username)
    else:
        resource.common.author.text = request.remote_addr
    resource.common.log_message.text = request.POST.get('log_message', '')

@register_creation_view(Wikitext)
@register_view(Wikitext, 'edit')
def edit_textwiki(request):
    if hasattr(request, 'ductus'):
        resource = request.ductus.resource
    else:
        resource = None

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

        if form.is_valid():
            if form.cleaned_data['text'].strip() == '':
                raise Exception
            if 'preview' in request.GET:
                pass # fixme
            if resource:
                resource = resource.clone()
            else:
                resource = Wikitext()
            resource.text = form.cleaned_data['text'].replace('\r', '')
            add_author_and_log_message(request, resource)
            urn = resource.save()
            return SuccessfulEditRedirect(urn)

    else:
        if resource:
            form = WikiEditForm({'text': resource.text})
        else:
            form = WikiEditForm()

    captcha_html = ""
    if recaptcha is not None and not request.user.is_authenticated():
        captcha_html = recaptcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY,
                                             use_ssl=request.is_secure())

    return render_to_response('textwiki/edit_wiki.html', {
        'form': form,
        'captcha': mark_safe(captcha_html),
    }, context_instance=RequestContext(request))

new_textwiki = edit_textwiki
