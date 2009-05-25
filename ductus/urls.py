from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/front_page', 'permanent': False}),
    (r'^admin/', include(admin.site.urls)),
    (r'^urn/(?P<hash_type>[-_\w]+)/(?P<hash_digest>[-_\w]+)$', 'ductus.wiki.views.view_urn'),
    (r'^(wiki/.+)$', 'ductus.wiki.views.view_wikipage'),
    (r'^new/(.*)', 'ductus.wiki.views.creation_view'),
    (r'^(user/.*/.+)$', 'ductus.wiki.views.view_wikipage'),
    (r'^user/(.*)$', 'ductus.user.views.view_userpage'),
#    (r'^group/', include('ductus.group.urls')),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^create-account/$', 'ductus.user.views.user_creation'),
    (r'^change-password/$', 'django.contrib.auth.views.password_change'),
    (r'^change-password/success/$', 'django.contrib.auth.views.password_change_done'),
    (r'^reset-password/$', 'django.contrib.auth.views.password_reset'),
    (r'^reset-password/requested/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^reset-password/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset-password/success/$', 'django.contrib.auth.views.password_reset_complete'),
    (r'^setlang/$', 'django.views.i18n.set_language'),
)

if (settings.DEBUG
    and getattr(settings, "DUCTUS_MEDIA_PREFIX", "").startswith('/')
    and getattr(settings, "DUCTUS_MEDIA_ROOT", "")):
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.DUCTUS_MEDIA_PREFIX[1:], 'django.views.static.serve', {'document_root': settings.DUCTUS_MEDIA_ROOT}),
    )
