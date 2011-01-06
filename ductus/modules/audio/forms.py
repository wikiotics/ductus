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

import subprocess
import os
from tempfile import mkstemp

from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy, ugettext as _

from ductus.modules.audio.models import Audio
from ductus.resource import get_resource_database

OGGINFO_PATH = getattr(settings, "OGGINFO_PATH", '/usr/bin/ogginfo')

class AudioField(forms.FileField):
    default_error_messages = {
        'invalid_vorbis': _(u'Not a valid ogg/vorbis file.'),
        'file_too_large': _(u'The file you chose is too large.  Please select a file that contains fewer than %d bytes.'),
    }

    def clean(self, data, initial=None):
        rv = super(AudioField, self).clean(data, initial)

        # make sure the blob is small enough to fit in the ResourceDatabase
        # without raising SizeTooLargeError
        max_resource_size = get_resource_database().max_resource_size
        if data.size > max_resource_size:
            raise forms.ValidationError(self.error_messages['file_too_large'] % max_resource_size)

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

            # /dev/null exists only on unix systems, sadly; see
            # http://mail.python.org/pipermail/python-dev/2006-June/066111.html
            # for lack of a better solution
            devnull = file('/dev/null', 'w')
            try:
                retcode = subprocess.call([OGGINFO_PATH, '-q', '-q', filename],
                                          stdout=devnull, stderr=devnull)
                if retcode != 0:
                    raise forms.ValidationError(self.error_messages['invalid_vorbis'])

            finally:
                devnull.close()

            return rv

        finally:
            if filename_requires_cleanup:
                os.remove(filename)

class AudioImportForm(forms.Form):
    file = AudioField()

    def save(self, save_context):
        audio = Audio()
        audio.blob.store(iter(self.cleaned_data['file'].chunks()))
        audio.blob.mime_type = 'audio/ogg'
        audio.common.patch_from_blueprint(None, save_context)
        return audio.save()
