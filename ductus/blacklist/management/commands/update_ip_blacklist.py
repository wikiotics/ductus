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
from shutil import copyfile
from urllib2 import urlopen
from zipfile import ZipFile
from StringIO import StringIO
from socket import inet_aton

from django.conf import settings
from django.core.management.base import NoArgsCommand

from ductus.util import iterator_to_tempfile

class Command(NoArgsCommand):
    help = "download banned ip addresses and save to DUCTUS_BLACKLIST_FILE."

    def handle_noargs(self, **options):
        # obtain the list of banned ip addresses
        url = 'http://www.stopforumspam.com/downloads/bannedips.zip'
        csv_zip = urlopen(url).read()
        zipfile = ZipFile(StringIO(csv_zip))
        filename = zipfile.namelist()[0]
        csv_string = zipfile.read(filename)
        banned_ips = csv_string.strip(',').split(',')

        # rearrange things for efficient storage
        banned_ips = sorted(inet_aton(b) for b in banned_ips)
        banned_ips_bytes = b''.join(banned_ips)

        # save the banned ip list to disk
        output_filename = settings.DUCTUS_BLACKLIST_FILE
        if not output_filename:
            raise Exception
        tmpfile = iterator_to_tempfile([banned_ips_bytes])
        try:
            copyfile(tmpfile, output_filename)
        finally:
            os.remove(tmpfile)
