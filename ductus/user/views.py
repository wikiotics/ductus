from django.views.decorators.vary import vary_on_headers
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.views import login, logout, password_change, password_change_done
from django.contrib.auth.forms import UserCreationForm

def wrap(view):
    return vary_on_headers('Cookie', 'Accept-language')(view)

login = wrap(login)
logout = wrap(logout)
password_change = wrap(password_change)
password_change_done = wrap(password_change_done)

@wrap
def user_creation(request, template_name='registration/create_user.html',
                  success_template_name='registration/user_created.html'):
    "Displays user creation form and handles its action"
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render_to_response(success_template_name, {
                'username': form.cleaned_data["username"],
            }, context_instance=RequestContext(request))
    else:
        form = UserCreationForm()

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))
