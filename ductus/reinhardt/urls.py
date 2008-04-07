from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
#    (r'^group/', include('ductus.reinhardt.apps.group.urls')),
#    (r'^urn/', include('ductus.reinhardt.apps.urn.urls')),
#    (r'^user/', include('ductus.reinhardt.apps.user.urls')),
#    (r'^wiki/', include('ductus.reinhardt.apps.wiki.urls')),
)
