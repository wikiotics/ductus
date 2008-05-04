from django.http import HttpResponse
from ductus.apps.urn.views import register_view
from ductus.apps.urn import get_resource_database

from PIL import Image, ImageFile
from cStringIO import StringIO

__allowed_thumbnail_sizes = set([(250, 250)])

@register_view('{http://wikiotics.org/ns/2008/picture}picture', None)
def view_picture(request, requested_view, urn, tree):
    blob = tree.getroot().find('{http://wikiotics.org/ns/2008/picture}blob')
    blob_urn = blob.get('{http://www.w3.org/1999/xlink}href')
    mime_type = blob.get('type') # lxml does not seem to set the
                                 # namespace correctly on this element
                                 # when parsing.  Investigation is
                                 # needed.

    # fixme: set X-License header

    # prepare original image
    data_iterator = get_resource_database().get_blob(blob_urn)

    # resize if requested
    if 'max_size' in request.GET:
        try:
            max_width, max_height = [int(n) for n in
                                     request.GET['max_size'].split(',')]
        except Exception:
            raise # call this a formatting error or something
        if (max_width, max_height) not in __allowed_thumbnail_sizes:
            raise Exception("Requested size not available")

        p = ImageFile.Parser()
        for data in data_iterator:
            p.feed(data)
        im = p.close()
        im.thumbnail((max_width, max_height), Image.ANTIALIAS)
        output = StringIO()
        im.save(output, 'JPEG')
        data_iterator = iter([output.getvalue()])
        mime_type = 'image/jpeg'

    return HttpResponse(data_iterator,
                        content_type=mime_type)
