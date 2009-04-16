from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django import forms

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

    return render_to_response(template_name, {
        'form': form,
        'captcha': mark_safe(captcha_html),
    }, context_instance=RequestContext(request))

def view_userpage(request, username):
    user = get_object_or_404(User, username=username)
    return render_to_response("user/userpage.html", {
        'user': user,
    }, context_instance=RequestContext(request))
