from django.http import HttpResponse, Http404

from ductus.resource import determine_header
from ductus.apps.urn import get_resource_database

def view_urn(request, hash_type, hash_digest):
    urn = 'urn:%s:%s' % (hash_type, hash_digest)
    resource_database = get_resource_database()
    try:
        data_iterator = resource_database[urn]
    except KeyError:
        raise Http404
    header, data_iterator = determine_header(data_iterator)
    if request.GET['view'] == 'raw':
        return HttpResponse(data_iterator,
                            content_type='application/octet-stream')
    elif header == 'xml':
        del data_iterator
        tree = resource_database.get_xml_tree(urn)
        root_tag_name = tree.getroot().tag
        try:
            f = __registered_applets[root_tag_name]
            return f(request, urn, tree)
        except KeyError:
            raise Http404
    elif header == 'blob':
        if 'view' in request.GET:
            return HttpResponse("'view' not implemented for blobs")
        header, data_iterator = determine_header(data_iterator, False)
        return HttpResponse(data_iterator,
                            content_type='application/octet-stream')

    raise Http404

def register_applet(root_tag_name):
    def _register_applet(func):
        __registered_applets[root_tag_name] = func
        return func
    return _register_applet

__registered_applets = {}
