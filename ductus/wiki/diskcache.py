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

import os

from django.conf import settings

from ductus.resource.storage.local import split_urn

def __to_filename(urn, key):
    hash_type, digest = split_urn(urn)
    filename = os.path.join(settings.DUCTUS_DISKCACHE_DIR, hash_type,
                            digest[0:2], (digest[2:4] or digest[0:2]), digest)
    filename += '?' + key # fixme: encode if there are illegal characters
    return filename

def put(urn, key, data_iterator):
    if not hasattr(settings, "DUCTUS_DISKCACHE_DIR"):
        return False

    filename = __to_filename(urn, key)

    dirname = os.path.dirname(filename)
    try:
        os.makedirs(dirname, mode=0755)
    except OSError:
        # fail only if the directory doesn't already exist
        if not os.path.isdir(dirname):
            raise

    try:
        fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0644)
    except OSError:
        return False

    f = os.fdopen(fd, "wb")
    for data in data_iterator:
        f.write(data)
    f.close()
    return True

def get(urn, key):
    if not hasattr(settings, "DUCTUS_DISKCACHE_DIR"):
        return None

    filename = __to_filename(urn, key)
    try:
        f = file(filename, "rb")
        return iter(f)
    except (OSError, IOError):
        return None
