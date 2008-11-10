from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
#    (r'^group/', include('ductus.apps.group.urls')),
    (r'^urn/', include('ductus.apps.urn.urls')),
#    (r'^user/', include('ductus.apps.user.urls')),
    (r'^wiki/', include('ductus.apps.wiki.urls')),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^setlang/$', 'django.views.i18n.set_language'),
    (r'^new/picture/', 'ductus.applets.picture.edit_views.new_picture'),
    (r'^new/picture_choice/', 'ductus.applets.picture_choice.edit_views.new_picture_choice'),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/front_page/'}),
)

from ductus.resource.storage import LocalStorageBackend
storage_backend = LocalStorageBackend('/tmp/ductus')
