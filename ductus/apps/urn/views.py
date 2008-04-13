# Ductus
# Copyright (C) 2008  Jim Garrison <jim@garrison.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
