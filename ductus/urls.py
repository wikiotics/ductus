from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': settings.DUCTUS_FRONT_PAGE, 'permanent': False}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^urn/(?P<hash_type>[-_\w]+)/(?P<hash_digest>[-_\w]+)$', 'ductus.wiki.views.view_urn'),
    url(r'^(wiki/.+)$', 'ductus.wiki.views.view_wikipage'),
    url(r'^new/(.*)', 'ductus.wiki.views.creation_view'),
    url(r'^(user/.*/.+)$', 'ductus.wiki.views.view_wikipage'),
    url(r'^user/(.*)$', 'ductus.user.views.view_userpage'),
#    url(r'^group/', include('ductus.group.urls')),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),
    url(r'^create-account$', 'ductus.user.views.user_creation'),
    url(r'^account-settings$', 'ductus.user.views.account_settings'),
    url(r'^change-password$', 'django.contrib.auth.views.password_change'),
    url(r'^change-password/success$', 'django.contrib.auth.views.password_change_done'),
    url(r'^reset-password$', 'django.contrib.auth.views.password_reset'),
    url(r'^reset-password/requested$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset-password/confirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset-password/success$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^setlang$', 'django.views.i18n.set_language'),
)

if (settings.DEBUG and settings.DUCTUS_MEDIA_PREFIX.startswith('/')):
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.DUCTUS_MEDIA_PREFIX[1:], 'django.views.static.serve', {'document_root': settings.DUCTUS_SITE_ROOT + '/static'}),
    )
