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

    requested_view = request.GET.get('view', None)

    if requested_view == 'raw':
        return HttpResponse(data_iterator,
                            content_type='application/octet-stream')

    if header == 'blob':
        header, data_iterator = determine_header(data_iterator, False)
        return HttpResponse(data_iterator,
                            content_type='application/octet-stream')

    if header == 'xml':
        del data_iterator
        tree = resource_database.get_xml_tree(urn)
        root_tag_name = tree.getroot().tag
        try:
            f = __registered_applets[(root_tag_name, requested_view)]
            return f(request, requested_view, urn, tree)
        except KeyError:
            raise Http404

    raise Http404

def register_applet(root_tag_name, *args):
    if len(args) == 0:
        raise TypeError("function requires at least two arguments")
    def _register_applet(func):
        for arg in args:
            __registered_applets[(root_tag_name, arg)] = func
        return func
    return _register_applet

__registered_applets = {}
