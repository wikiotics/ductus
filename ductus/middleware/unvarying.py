class UnvaryingResponseMiddleware(object):
    def process_response(self, request, response):
        if getattr(response, "_unvarying", False):
            try:
                del response["Vary"]
            except KeyError:
                pass
        else:
            from django.utils.cache import patch_cache_control
            patch_cache_control(response, private=True)
        return response
