from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^urn/', include('ductus.reinhardt.apps.urn.urls')),
)
