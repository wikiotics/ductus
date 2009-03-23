from ductus.wiki import SuccessfulEditRedirect
from ductus.util.http import render_json_response

class DuctusCommonMiddleware(object):
    def process_response(self, request, response):
        if request.is_ajax() and isinstance(response, SuccessfulEditRedirect):
            response = render_json_response({"urn": response.urn})
        return response
