from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root), # Should be changed in Django 1.1
#    (r'^group/', include('ductus.group.urls')),
    (r'^urn/', include('ductus.urn.urls')),
#    (r'^user/', include('ductus.user.urls')),
    (r'^wiki/', include('ductus.wiki.urls')),
    (r'^login/$', 'ductus.user.views.login'),
    (r'^logout/$', 'ductus.user.views.logout'),
    (r'^create-account/$', 'ductus.user.views.user_creation'),
    (r'^change-password/$', 'ductus.user.views.password_change', {'post_change_redirect': '/change-password/success/'}),
    (r'^change-password/success/$', 'ductus.user.views.password_change_done'),
    (r'^setlang/$', 'django.views.i18n.set_language'),
    (r'^new/picture/', 'ductus.applets.picture.edit_views.new_picture'),
    (r'^new/picture_choice/', 'ductus.applets.picture_choice.edit_views.new_picture_choice'),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/wiki/front_page/'}), # django 1.1: add {'permanent': False} to this dictionary
)

from ductus.resource.storage import LocalStorageBackend
storage_backend = LocalStorageBackend('/tmp/ductus')

try:
    from ductus_local_urls import *
except ImportError:
    pass
