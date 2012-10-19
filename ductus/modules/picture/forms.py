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

import logging
import re
import os
from tempfile import mkstemp

from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext as _

from ductus.resource import get_resource_database, UnsupportedURN
from ductus.wiki import resolve_urn
from ductus.modules.picture.ductmodels import Picture

logger = logging.getLogger(__name__)

class PictureRotationForm(forms.Form):
    choices = (
        (None, 'Use image metadata'),
        (0, 'No rotation'),
        (90, '90 degrees counterclockwise'),
        (180, '180 degrees'),
        (270, '90 degrees clockwise'),
    )

    rotation = forms.ChoiceField(choices=choices)

class PictureFileField(forms.FileField):
    """a field for uploading picture files directly from the client into the resource db."""

    def clean(self, data, initial=None):
        rv = super(PictureFileField, self).clean(data, initial)
        # make sure the blob is small enough to fit in the ResourceDatabase
        # without raising SizeTooLargeError
        max_blob_size = get_resource_database().max_blob_size
        if data.size > max_blob_size:
            raise forms.ValidationError(self.error_messages['file_too_large'] % max_blob_size)

        filename_requires_cleanup = False

        try:
            if hasattr(data, 'temporary_file_path'):
                filename = data.temporary_file_path()
            else:
                fd, filename = mkstemp()
                filename_requires_cleanup = True
                f = os.fdopen(fd, 'wb')
                try:
                    for chunk in data.chunks():
                        f.write(chunk)
                finally:
                    f.close()

            from magic import Magic
            mime_type = Magic(mime=True).from_file(filename)
            try:
                logger.debug("Mime type detected: %s", mime_type)
            except KeyError:
                raise forms.ValidationError(self.error_messages['unrecognized_file_type'])

            #TODO: double check the file type, like we do for audio files
            rv.ductus_mime_type = mime_type
            return rv

        finally:
            if filename_requires_cleanup:
                os.remove(filename)

class PictureImportForm(forms.Form):

    # the form validator makes sure that one of the fields below is provided
    uri = forms.CharField(required=False)
    file = PictureFileField(required=False)

    _uri_handlers = []

    @classmethod
    def register_uri_handler(cls, handler):
        cls._uri_handlers.append(handler)
        return handler

    def clean_uri(self):
        uri = self.cleaned_data['uri']
        if uri:
            for handler_class in self._uri_handlers:
                if handler_class.handles(uri):
                    handler = handler_class(uri)
                    handler.validate()
                    self.handler = handler
                    return uri
            raise forms.ValidationError(_("Unrecognized uri type"))
        else:
            return u''

    def save(self, save_context):
        if self.cleaned_data['uri'] != '':
            # either we have a uri (like a flickr picture)
            return self.handler.save(save_context)
        if self.cleaned_data['file'] is not None:
            # or it's a local file we need to save
            pic = Picture()
            pic.blob.store(iter(self.cleaned_data['file'].chunks()))
            pic.blob.mime_type = self.cleaned_data['file'].ductus_mime_type
            pic.common.patch_from_blueprint(None, save_context)
            return pic.save()

    @classmethod
    def get_verbose_input_descriptions(cls):
        return [handler.verbose_description for handler in cls._uri_handlers
                if hasattr(handler, "verbose_description")]

@PictureImportForm.register_uri_handler
class UrnHandler(object):
    "uri handler for urn: uris as well as local /urn/* urls"

    _re_objects = (
        re.compile(r'.*\/urn\/(sha384)\/([A-Za-z0-9\-_]{64}).*'),
        re.compile(r'urn\:(sha384)\:([A-Za-z0-9\-_]{64})'),
    )

    verbose_description = ugettext_lazy("a URN available on this site")

    @classmethod
    def handles(cls, uri):
        return any(r.match(uri) for r in cls._re_objects)

    def __init__(self, uri):
        self.uri = uri

    def validate(self):
        from ductus.resource import get_resource_database
        from ductus.resource.ductmodels import DuctModelMismatchError
        resource_database = get_resource_database()

        for r in self._re_objects:
            match = r.match(self.uri)
            if match is not None:
                hash_type, digest = match.group(1), match.group(2)
                urn = "urn:%s:%s" % (hash_type, digest)
                if urn not in resource_database:
                    raise forms.ValidationError(_(u"This urn cannot be found on the server you are currently accessing."))
                try:
                    Picture.load(urn)
                except DuctModelMismatchError:
                    raise forms.ValidationError(_(u"This urn represents content that is not a picture."))
                # fixme: handle exception raised by get_resource_object if it's
                # actually a blob
                self.urn = urn
                return

        # this should never be reached
        assert self.handles(self.uri)

    def save(self, save_context):
        return self.urn
