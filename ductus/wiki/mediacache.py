# Ductus
# Copyright (C) 2009  Jim Garrison <jim@garrison.cc>
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

import re
import os
from shutil import copyfile

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404

from ductus.resource import get_resource_database, split_urn
from ductus.utils import iterator_to_tempfile
from ductus.utils.http import StreamingHttpResponse
from ductus.wiki import registered_mediacache_views
from ductus.decorators import unvarying

# the whole mediacache subsystem currently assumes that there are no illegal
# characters in additional_args.  if we later decide we want to allow illegal
# characters in additional_args, we will need to think about escaping things
# throughout this file.

MEDIACACHE_VIEW_DISABLED = getattr(settings, "MEDIACACHE_VIEW_DISABLED", False)

mime_types = (
    ('jpg', 'image/jpeg'),
    ('oga', 'audio/ogg'),
    ('m4a', 'audio/mp4'),
    ('webma', 'audio/webm'),
)
ext_to_mime = dict(mime_types)
mime_to_ext = dict([(_b, _a) for (_a, _b) in mime_types])

def _dotstr(additional_args):
    if additional_args:
        return '.' + additional_args
    else:
        return ''

_pathname_re = re.compile(r'^(?P<hash_type>\w+)/(?P<digest>[A-Za-z0-9_-]+)(?:\.(?P<additional_args>\w+))?\.(?P<extension>\w+)$')
_alternate_pathname_re = re.compile(r'^(?P<hash_type>\w+)/([A-Za-z0-9_-]{2})/([A-Za-z0-9_-]{2})/(?P<digest>\2\3[A-Za-z0-9_-]+)(?:\.(?P<additional_args>\w+))?\.(?P<extension>\w+)$')
_legal_additional_args_re = re.compile(r'^[\w]*$')

@unvarying
def mediacache_django_view(request, pathname):
    if MEDIACACHE_VIEW_DISABLED:
        raise Http404("mediacache view is not enabled")

    return _mediacache_view(pathname, request.META['QUERY_STRING'])

def mediacache_wsgi_view(*args):
    raise NotImplementedError
    try:
        return _mediacache_view(pathname, query_string)
    except Http404:
        return None  # fixme

def _mediacache_view(pathname, query_string):
    m = _pathname_re.match(pathname) or _alternate_pathname_re.match(pathname)
    if m is None:
        raise Http404("pathname does not match mediacache re")

    hash_type = m.group('hash_type')
    digest = m.group('digest')
    additional_args = m.group('additional_args')
    extension = m.group('extension')

    try:
        mime_type = ext_to_mime[extension]
    except KeyError:
        raise Http404("unknown extension")

    blob_urn = 'urn:%s:%s' % (hash_type, digest)

    # if the file exists on the filesystem, serve it!
    data_iterator = get(blob_urn, mime_type, additional_args)
    if data_iterator:
        # fixme: possibly log a warning if we're in deploy mode
        response = StreamingHttpResponse(data_iterator, content_type=mime_type)
        response["X-Ductus-Mediacache"] = "served"
        return response

    if not query_string:
        raise Http404("the urn of the resource that references this blob should be given as the query string")

    resource_database = get_resource_database()
    try:
        resource = resource_database.get_resource_object(query_string)
    except KeyError:
        raise Http404("the query string does not reference an existing urn")

    return _do_mediacache_view_serve(blob_urn, mime_type, additional_args, resource)

def mediacache_redirect(request, blob_urn, mime_type, additional_args, resource):
    """Redirect to a mediacache resource

    This will issue a redirect to the mediacache url that serves this resource,
    given by DUCTUS_MEDIACACHE_URL.  If DUCTUS_MEDIACACHE_URL is not defined,
    it will be assumed to be '/mediacache'.
    """

    # as an additional layer of protection, make sure each mediacache module
    # view doesn't allow the insertion of rogue characters into additional_args
    if additional_args:
        if not _legal_additional_args_re.match(additional_args):
            raise Exception("illegal characters given in additional_args!")

    hash_type, digest = split_urn(blob_urn)

    pathname = "%s/%s%s.%s" % (hash_type, digest,
                               _dotstr(additional_args),
                               mime_to_ext[mime_type])

    if request.is_secure() and getattr(settings, "DUCTUS_MEDIACACHE_URL_SECURE", None):
        mediacache_url = settings.DUCTUS_MEDIACACHE_URL_SECURE
    elif settings.DUCTUS_MEDIACACHE_URL:
        mediacache_url = settings.DUCTUS_MEDIACACHE_URL
    else:
        mediacache_url = '/mediacache'

    url = "%s/%s?%s" % (mediacache_url, pathname, resource.urn)
    return HttpResponseRedirect(url)

def _do_mediacache_view_generate(blob_urn, mime_type, additional_args, resource):
    # call the mediacache view to generate the bits
    mcv = registered_mediacache_views[resource.fqn]
    data_iterator = mcv(blob_urn, mime_type, additional_args, resource)
    if data_iterator is None:
        raise Http404("mediacache view returned None")

    # store to filesystem
    data_iterator = list(data_iterator) # fixme: this is suboptimal now that django #6527 is fixed
    if getattr(settings, "DUCTUS_MEDIACACHE_DIR"):
        # fixme: log a warning if this returns False (i.e. an error occurred)
        put(blob_urn, mime_type, additional_args, data_iterator)

    return data_iterator

def _do_mediacache_view_serve(blob_urn, mime_type, additional_args, resource):
    data_iterator_list = _do_mediacache_view_generate(blob_urn, mime_type, additional_args, resource)
    # send it off
    response = HttpResponse(data_iterator_list, content_type=mime_type) # see django #6527
    response["X-Ductus-Mediacache"] = "generated"
    return response

def get_generated_filename(blob_urn, mime_type, additional_args, resource):
    # if the mediacache is ever /not/ stored directly in the filesystem, we
    # will need to make this function return a temporary file instead (and we
    # will need to worry about deleting said file)

    filename = __to_filename(blob_urn, mime_type, additional_args)

    import os.path
    if not os.path.isfile(filename):
        _do_mediacache_view_generate(blob_urn, mime_type, additional_args, resource)

    return filename

def __to_filename(urn, mime_type, additional_args):
    hash_type, digest = split_urn(urn)
    extension = mime_to_ext[mime_type]

    basename = "%s%s.%s" % (digest, _dotstr(additional_args), extension)
    # fixme: assert that there are no illegal characters in filename
    filename = os.path.join(settings.DUCTUS_MEDIACACHE_DIR, hash_type,
                            digest[0:2], (digest[2:4] or digest[0:2]), basename)
    return filename

def put(urn, mime_type, additional_args, data_iterator):
    filename = __to_filename(urn, mime_type, additional_args)

    dirname = os.path.dirname(filename)
    try:
        os.makedirs(dirname, mode=0755)
    except OSError:
        # fail only if the directory doesn't already exist
        if not os.path.isdir(dirname):
            raise

    tmpfile = iterator_to_tempfile(data_iterator)
    try:
        copyfile(tmpfile, filename)
    except OSError:
        return False
    finally:
        os.remove(tmpfile)

    return True

def get(urn, mime_type, additional_args):
    if not hasattr(settings, "DUCTUS_MEDIACACHE_DIR"):
        return None

    filename = __to_filename(urn, mime_type, additional_args)
    try:
        f = file(filename, "rb")
        return iter(f)
    except (OSError, IOError):
        return None

def resolve_relative_mediacache_url(resource, mime_type=None, additional_args=None, blob_urn=None):
    hash_type, digest = split_urn(blob_urn or resource.blob.href)
    ext = mime_to_ext[mime_type or resource.blob.mime_type]
    return "%s/%s%s.%s?%s" % (hash_type, digest, _dotstr(additional_args),
                              ext, resource.urn)
