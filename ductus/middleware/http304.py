from django.http import HttpResponseNotModified
from ductus.util.http import Http304

class Http304ExceptionHandlerMiddleware(object):
    def process_exception(self, request, exception):
        if exception == Http304:
            return HttpResponseNotModified()
