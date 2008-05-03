from django.http import HttpResponse
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database

@register_view('{http://wikiotics.org/ns/2008/picture}picture', None)
def view_picture(request, requested_view, urn, tree):
    blob = tree.getroot().find('{http://wikiotics.org/ns/2008/picture}blob')
    blob_urn = blob.get('{http://www.w3.org/1999/xlink}href')
    mime_type = blob.get('type') # lxml does not seem to set the
                                 # namespace correctly on this element
                                 # when parsing.  Investigation is
                                 # needed.

    # fixme: set X-License header

    # send blob as image
    data_iterator = get_resource_database().get_blob(blob_urn)
    return HttpResponse(data_iterator,
                        content_type=mime_type)
