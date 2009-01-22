from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.forms import UserCreationForm

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
