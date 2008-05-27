from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
#    (r'^group/', include('ductus.apps.group.urls')),
    (r'^urn/', include('ductus.apps.urn.urls')),
#    (r'^user/', include('ductus.apps.user.urls')),
#    (r'^wiki/', include('ductus.apps.wiki.urls')),
    (r'^new/picture/', 'ductus.applets.picture.edit_views.new_picture'),
)

from ductus.resource.storage import LocalStorageBackend
storage_backend = LocalStorageBackend('/tmp/ductus')
