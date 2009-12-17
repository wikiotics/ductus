from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote

from ductus.wiki import SuccessfulEditRedirect
from ductus.util.http import render_json_response, ImmediateResponse

class DuctusCommonMiddleware(object):
    "Utility middleware for common Ductus tricks"

    def process_request(self, request):
        "Sets request.escaped_full_path on each request"
        request.escaped_full_path = iri_to_uri(urlquote(request.path))
        if request.META.get("QUERY_STRING", ''):
            request.escaped_full_path += u'?' + iri_to_uri(request.META["QUERY_STRING"])

    def process_response(self, request, response):
        "Handles successful ajax edits"
        if request.is_ajax() and isinstance(response, SuccessfulEditRedirect):
            response = render_json_response({"urn": response.urn})
        return response

    def process_exception(self, request, exception):
        "Handles ImmediateResponse exception"
        if isinstance(exception, ImmediateResponse):
            return exception.response
