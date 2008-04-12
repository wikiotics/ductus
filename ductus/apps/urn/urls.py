from django.conf.urls.defaults import *

urlpatterns = patterns('ductus.apps.urn.views',
   (r'^(?P<hash_type>[_-\w]+)/(?P<hash_digest>[_-\w]+)/$', 'view_urn'),
)
