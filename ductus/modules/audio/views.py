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

import os
from shutil import rmtree
import subprocess
from tempfile import mkdtemp
import logging
import hashlib

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy

from ductus.resource.ductmodels import BlueprintSaveContext
from ductus.resource import get_resource_database
from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view, register_view, register_mediacache_view
from ductus.wiki.mediacache import mediacache_redirect, mime_to_ext, resolve_relative_mediacache_url, get_generated_filename
from ductus.decorators import unvarying
from ductus.modules.audio.ductmodels import Audio
from ductus.modules.audio.forms import AudioImportForm
from ductus.util.http import render_json_response
from ductus.util import iterator_to_tempfile, iterate_file_then_delete

AUDIO_CONVERSION_COMMANDS = getattr(settings, "AUDIO_CONVERSION_COMMANDS", None) or {}

logger = logging.getLogger(__name__)

available_audio_formats = {}
for __in, __out in AUDIO_CONVERSION_COMMANDS.keys():
    available_audio_formats.setdefault(__in, []).append(__out)

@register_creation_view(Audio, description=ugettext_lazy('a standalone audio file'), category='standalone-media')
def new_audio(request):
    if request.method == 'POST':
        form = AudioImportForm(request.POST, request.FILES)
        if form.is_valid():
            save_context = BlueprintSaveContext.from_request(request)
            urn = form.save(save_context)
            return SuccessfulEditRedirect(urn)
        else:
            if request.is_ajax():
                return render_json_response({'errors': form.errors})
    else:
        form = AudioImportForm()

    return render_to_response('audio/audio_import_form.html', {
        'form': form,
    }, RequestContext(request))

@register_view(Audio, 'audio')
@unvarying
def view_audio(request):
    audio = request.ductus.resource

    return mediacache_redirect(request, audio.blob.href, audio.blob.mime_type,
                               '', audio)

@register_view(Audio)
def view_audio_info(request):
    return render_to_response('audio/display.html', {
        'available_audio_formats': available_audio_formats,
    }, RequestContext(request))

@register_view(Audio, 'edit')
def edit_audio(request):
    return render_to_response('audio/edit.html', {
        'creation_view_key': 'audio',
    }, RequestContext(request))

@register_mediacache_view(Audio)
def mediacache_audio(blob_urn, mime_type, additional_args, audio):
    if additional_args:
        return None
    if blob_urn != audio.blob.href:
        return None

    if mime_type == audio.blob.mime_type:
        return iter(audio.blob)

    input_suffix = '.' + mime_to_ext[audio.blob.mime_type]
    output_suffix = '.' + mime_to_ext[mime_type]
    try:
        cmd = AUDIO_CONVERSION_COMMANDS[(audio.blob.mime_type, mime_type)]
    except KeyError:
        return None # we don't support this converstion
    else:
        input_filename = iterator_to_tempfile(iter(audio.blob), suffix=input_suffix)
        try:
            tmpdir = mkdtemp()
            def delete_tmpdir(filename=None):
                rmtree(tmpdir, ignore_errors=True)
            output_filename = os.path.join(tmpdir, "audio" + output_suffix)
            logger.info("Converting %s to %s", input_filename, output_filename)
            cmd = cmd.format(input_filename=input_filename,
                             output_filename=output_filename)
            try:
                subprocess.check_call(cmd, shell=True)
            except Exception:
                delete_tmpdir()
                raise
            return iterate_file_then_delete(output_filename, delete_func=delete_tmpdir)
        finally:
            os.remove(input_filename)

def _join_list(lst, c):
    """Returns a new list with `c` between each element"""
    from itertools import chain, izip, repeat
    rv = list(chain.from_iterable(izip(lst, repeat(c))))
    try:
        rv.pop()
    except IndexError:
        pass
    return rv

def get_joined_audio_mediacache_url(resource, audio_urn_list, mime_type):
    """Returns relative urls, meant to have the mediacache prefix prepended"""
    assert mime_type in ('audio/webm', 'audio/mp4')

    if not audio_urn_list:
        return None

    first_audio_resource = get_resource_database().get_resource_object(audio_urn_list[0])

    if len(audio_urn_list) == 1:
        return resolve_relative_mediacache_url(first_audio_resource)
    else:
        urn_list_hash = hashlib.sha1(' '.join(audio_urn_list)).hexdigest()
        return resolve_relative_mediacache_url(resource, mime_type, urn_list_hash, first_audio_resource.blob.href)

def mediacache_cat_audio(first_blob_urn, audio_urn_list, mime_type):
    if len(audio_urn_list) < 2:
        # there's no reason to do concatenation...
        # get_joined_audio_mediacache_url() points to the original (single)
        # file anyway
        return None

    resource_database = get_resource_database()
    audio_resources = [resource_database.get_resource_object(urn)
                       for urn in audio_urn_list]
    if audio_resources[0].blob.href != first_blob_urn:
        return None

    if mime_type == 'audio/webm':
        return _cat_webm(audio_resources)
    elif mime_type == 'audio/mp4':
        return _cat_m4a(audio_resources)
    else:
        raise Exception("attempting to concatenate unsupported format: %s" % mime_type)

def _cat_webm(audio_resources):
    filenames = [get_generated_filename(resource.blob.href, 'audio/ogg',
                                        None, resource)
                 for resource in audio_resources]

    # join the audio files into one
    tmpdir = mkdtemp()
    def delete_tmpdir(filename=None):
        rmtree(tmpdir, ignore_errors=True)
    output_filename = os.path.join(tmpdir, "joined_audio.webm")
    logger.info("Joining %d ogg/vorbis files" % len(filenames))
    try:
        subprocess.check_call([settings.MKVMERGE_PATH, '-o', output_filename, '-w', '-q'] + _join_list(filenames, '+'))
    except Exception:
        delete_tmpdir()
        raise
    return iterate_file_then_delete(output_filename, delete_func=delete_tmpdir)

def _cat_m4a(audio_resources):
    filenames = [get_generated_filename(resource.blob.href, 'audio/mp4',
                                        None, resource)
                 for resource in audio_resources]

    # join the audio files into one
    tmpdir = mkdtemp()
    def delete_tmpdir(filename=None):
        rmtree(tmpdir, ignore_errors=True)
    output_filename = os.path.join(tmpdir, "joined_audio.m4a")
    logger.info("Joining %d m4a files" % len(filenames))
    try:
        # MP4Box can concatenate a maximum of 20 files at a time, so we call it
        # repeatedly until everything is concatenated.
        from itertools import islice
        MAX_CUMUL_OPS = 20  # as defined in gpac/applications/mp4box/main.c
        i = iter(filenames)
        while True:
            current_filenames = list(islice(i, MAX_CUMUL_OPS))
            if not current_filenames:
                break
            cmd = [settings.MP4BOX_PATH, output_filename, '-cat'] + _join_list(current_filenames, '-cat')
            subprocess.check_call(cmd)
    except Exception:
        delete_tmpdir()
        raise
    return iterate_file_then_delete(output_filename, delete_func=delete_tmpdir)
