from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django import forms

from ductus.user.forms import UserEditForm

recaptcha = None
if hasattr(settings, "RECAPTCHA_PRIVATE_KEY"):
    from recaptcha.client import captcha as recaptcha

def user_creation(request, template_name='registration/create_user.html',
                  success_template_name='registration/user_created.html'):
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
            return render_to_response(success_template_name, {
                'username': form.cleaned_data["username"],
            }, context_instance=RequestContext(request))
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

@login_required
def account_settings(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_("Your account settings have been updated."))
            return redirect(request.user)
    else:
        form = UserEditForm(instance=request.user)

    return render_to_response("user/user_form.html", {
        'form': form,
    }, RequestContext(request))

def view_userpage(request, username):
    user = get_object_or_404(User, username=username)
    return render_to_response("user/userpage.html", {
        'userpage_user': user,
    }, context_instance=RequestContext(request))
