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

from ductus.modules.audio.ductmodels import Audio
from ductus.resource import get_resource_database

OGGINFO_PATH = getattr(settings, "OGGINFO_PATH", '/usr/bin/ogginfo')
FAAD_PATH = getattr(settings, "FAAD_PATH", '/usr/bin/faad')

try:
    DEVNULL = subprocess.DEVNULL
except AttributeError:
    DEVNULL = subprocess.PIPE

def verify_aac_lc(filename, error_messages):
    popen = subprocess.Popen([FAAD_PATH, '-i', filename],
                             stdout=DEVNULL, stderr=subprocess.PIPE)
    stderr_output = popen.communicate()[1]

    if "LC AAC" not in stderr_output:
        raise forms.ValidationError(error_messages['invalid_lc_aac'])

    return 'audio/mp4'

def verify_ogg_vorbis(filename, error_messages):
    popen = subprocess.Popen([OGGINFO_PATH, filename],
                             stdout=subprocess.PIPE, stderr=DEVNULL)
    lower_stdout = popen.communicate()[0].lower()

    if popen.returncode != 0 or 'vorbis' not in lower_stdout:
        raise forms.ValidationError(error_messages['invalid_vorbis'])
    if 'theora' in lower_stdout:
        raise forms.ValidationError(error_messages['theora_stream_included'])

    return 'audio/ogg'

verification_map = {
    'audio/ogg': verify_ogg_vorbis,
    'application/ogg': verify_ogg_vorbis,
    'audio/mp4': verify_aac_lc,
}

class AudioField(forms.FileField):
    default_error_messages = {
        'unrecognized_file_type': _(u'Unrecognized file type.  Please upload an ogg/vorbis file or mp4/AAC file.'),
        'invalid_vorbis': _(u'Not a valid ogg/vorbis file.'),
        'invalid_lc_aac': _(u'Not a valid low-complexity AAC file in mp4 container.'),
        'theora_stream_included': _(u'The given file contains a theora (video) stream, but only audio is expected.'),
        'file_too_large': _(u'The file you chose is too large.  Please select a file that contains fewer than %d bytes.'),
    }

    def clean(self, data, initial=None):
        rv = super(AudioField, self).clean(data, initial)

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
                verify_file_type = verification_map[mime_type]
            except KeyError:
                raise forms.ValidationError(self.error_messages['unrecognized_file_type'])

            mime_type = verify_file_type(filename, self.error_messages)
            rv.ductus_mime_type = mime_type

            return rv

        finally:
            if filename_requires_cleanup:
                os.remove(filename)

class AudioImportForm(forms.Form):
    file = AudioField()

    def save(self, save_context):
        audio = Audio()
        audio.blob.store(iter(self.cleaned_data['file'].chunks()))
        audio.blob.mime_type = self.cleaned_data['file'].ductus_mime_type
        audio.common.patch_from_blueprint(None, save_context)
        return audio.save()
