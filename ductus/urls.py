from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

class TextTemplateView(TemplateView):
    def render_to_response(self, context, **kwargs):
        kwargs['content_type'] = 'text/plain'
        return super(TemplateView, self).render_to_response(context, **kwargs)

urlpatterns = patterns('',
    url(r'^$', 'ductus.wiki.views.view_frontpage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mediacache/(.*)$', 'ductus.wiki.mediacache.mediacache_django_view'),
    url(r'^new/?$', 'ductus.wiki.views.new_wikipage'),
    url(r'^robots\.txt$', TextTemplateView.as_view(template_name="robots.txt")),
    url(r'^login$', 'ductus.user.views.login'),
    url(r'^logout$', 'ductus.user.views.logout'),
    url(r'^create-account$', 'ductus.user.views.user_creation'),
    url(r'^account-settings$', 'ductus.user.views.account_settings'),
    url(r'^change-password$', 'django.contrib.auth.views.password_change'),
    url(r'^change-password/success$', 'django.contrib.auth.views.password_change_done'),
    url(r'^reset-password$', 'django.contrib.auth.views.password_reset'),
    url(r'^reset-password/requested$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset-password/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset-password/success$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^setlang$', 'django.views.i18n.set_language'),
    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', {'domain': 'djangojs', 'packages': ('ductus',)}),
    # this must come last since it matches practically everything...
    url(r'^(?P<prefix>\w+)/(?P<pagename>.+)$', 'ductus.wiki.views.wiki_dispatch'),
)
