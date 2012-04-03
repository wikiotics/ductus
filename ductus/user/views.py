# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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
from django.utils.translation import ugettext_lazy, ugettext as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as perform_login
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.contrib import messages
from django.utils.safestring import mark_safe
from django import forms

from ductus.wiki.models import WikiPage
from ductus.wiki.views import RegularWikiNamespace
from ductus.user.models import UserProfile
from ductus.user.forms import UserEditForm, UserProfileEditForm, UserCreationForm

recaptcha = None
if hasattr(settings, "RECAPTCHA_PRIVATE_KEY"):
    from recaptcha.client import captcha as recaptcha

def user_creation(request, template_name='registration/create_user.html'):
    "Displays user creation form and handles its action"
    if request.method == "POST":
        if recaptcha is not None:
            if not ('recaptcha_challenge_field' in request.POST
                    and 'recaptcha_response_field' in request.POST
                    and recaptcha.submit(request.POST['recaptcha_challenge_field'],
                                         request.POST['recaptcha_response_field'],
                                         settings.RECAPTCHA_PRIVATE_KEY,
                                         request.remote_addr).is_valid):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("invalid captcha")

        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # log in the user automatically
            user = authenticate(username=form.cleaned_data["username"],
                                password=form.cleaned_data["password1"])
            perform_login(request, user)
            return redirect("ductus.wiki.views.view_frontpage")
    else:
        form = UserCreationForm()

    captcha_html = ""
    if recaptcha is not None:
        captcha_html = recaptcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY,
                                             use_ssl=request.is_secure())
        captcha_html = captcha_html.replace('frameborder="0"',
                                            'style="border: 0"')

    return render_to_response(template_name, {
        'form': form,
        'captcha': mark_safe(captcha_html),
    }, context_instance=RequestContext(request))

def login(request):
    return django_login(request)

def logout(request):
    response = django_logout(request, next_page='/')
    #messages.info(request, _("You have been logged out."))
    return response

@login_required
def account_settings(request):
    if request.method == 'POST':
        userform = UserEditForm(request.POST, instance=request.user)
        profileform = UserProfileEditForm(request.POST, instance=request.user.profile)
        if userform.is_valid() and profileform.is_valid():
            userform.save()
            profileform.save()
            messages.success(request, _('Your account settings have been updated.'))
            return redirect(request.user)
    else:
        userform = UserEditForm(instance=request.user)
        profileform = UserProfileEditForm(instance=request.user.profile)

    return render_to_response("user/user_form.html", {
        'userform': userform,
        'profileform': profileform,
    }, RequestContext(request))

class UserNamespace(RegularWikiNamespace):
    def page_exists(self, pagename):
        if '/' not in pagename:
            try:
                if User.objects.get(username=pagename).is_active:
                    return True
            except User.DoesNotExist:
                pass

        return super(UserNamespace, self).page_exists(pagename)

    def allow_edit(self, user, pagename):
        return (user.is_authenticated()
                and user.is_active
                and pagename.partition('/')[0] == user.username)

    def view_page(self, request, pagename):
        if '/' not in pagename:
            user = get_object_or_404(User, username=pagename)
            pages_contributed_to = WikiPage.objects.filter(wikirevision__author=user).distinct().order_by('name')
            return render_to_response("user/userpage.html", {
                'userpage_user': user,
                'pages_contributed_to': pages_contributed_to,
            }, context_instance=RequestContext(request))
        else:
            return super(UserNamespace, self).view_page(request, pagename)

UserNamespace('user')
