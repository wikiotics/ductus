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

import json

from django.http import HttpResponse
from django.template import RequestContext, loader

def render_json_response(d):
    """Returns a HttpResponse with a json representation of the passed object"""
    return HttpResponse(json.dumps(d), content_type='application/json; charset=utf-8')

def query_string_not_found(request):
    """Used instead of Http404 if the query string causes nothing to be found.
    """

    t = loader.get_template('query_string_404.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=404)

class ImmediateResponse(Exception):
    def __init__(self, response, *args, **kwargs):
        if not isinstance(response, HttpResponse):
            response = HttpResponse(response, *args, **kwargs)
        elif args or kwargs:
            raise TypeError("too many arguments")
        self.response = response
