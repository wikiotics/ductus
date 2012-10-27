# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
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

from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.http import HttpRequest

from ductus.wiki import SuccessfulEditRedirect
from ductus.utils.http import render_json_response, ImmediateResponse

class DuctusCommonMiddleware(object):
    "Utility middleware for common Ductus tricks"

    def process_response(self, request, response):
        "Handles successful ajax edits"
        if request.is_ajax() and isinstance(response, SuccessfulEditRedirect):
            d = {"urn": response.urn}
            if "Location" in response:
                d["page_url"] = response["Location"]
            response = render_json_response(d)
        return response

    def process_exception(self, request, exception):
        "Handles ImmediateResponse exception"
        if isinstance(exception, ImmediateResponse):
            return exception.response

def __escaped_full_path(request, **kwargs):
    """Escaped path that includes the QUERY_STRING

    See http://code.ductus.us/ticket/32

    If kwargs are given, it is possible to override GET parameters in the
    returned path.
    """
    path = iri_to_uri(urlquote(request.path))
    if kwargs:
        GET = request.GET.copy()
        for k, v in kwargs.items():
            if v is None:
                GET.pop(k, None)
            else:
                GET[k] = v
        if GET:
            path += u'?' + GET.urlencode()
    elif request.META.get("QUERY_STRING"):
        path += u'?' + iri_to_uri(request.META["QUERY_STRING"])
    return path
HttpRequest.escaped_full_path = __escaped_full_path
