from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
#    (r'^group/', include('ductus.apps.group.urls')),
    (r'^urn/', include('ductus.apps.urn.urls')),
#    (r'^user/', include('ductus.apps.user.urls')),
#    (r'^wiki/', include('ductus.apps.wiki.urls')),
)

from ductus.resource.storage import LocalStorageBackend
resource_database = LocalStorageBackend('/tmp/ductus')
