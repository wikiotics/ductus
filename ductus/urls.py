from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root), # Should be changed in Django 1.1
#    (r'^group/', include('ductus.group.urls')),
    (r'^urn/', include('ductus.urn.urls')),
#    (r'^user/', include('ductus.user.urls')),
    (r'^wiki/', include('ductus.wiki.urls')),
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
    (r'^new/picture/', 'ductus.applets.picture.edit_views.new_picture'),
    (r'^new/picture_choice/', 'ductus.applets.picture_choice.edit_views.new_picture_choice'),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/front_page'}), # django 1.1: add {'permanent': False} to this dictionary
)

from ductus.resource.storage import LocalStorageBackend
storage_backend = LocalStorageBackend('/tmp/ductus')

try:
    from ductus_local_urls import *
except ImportError:
    pass
