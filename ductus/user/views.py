from django.views.decorators.vary import vary_on_headers
import django.contrib.auth.views

def wrap(view):
    return vary_on_headers('Cookie', 'Accept-language')(view)

login = wrap(django.contrib.auth.views.login)
logout = wrap(django.contrib.auth.views.logout)
