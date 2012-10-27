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

import pprint
from urllib2 import urlopen

def fetch_language_subtag_registry(url=None):
    """This should be called from a script and saved in data.py for further use"""
    if url is None:
        url = 'http://www.iana.org/assignments/language-subtag-registry'
    subtag_registry = urlopen(url).read().decode("utf-8")
    subtags = subtag_registry.split("%%")
    file_date = subtags.pop(0).strip()
    db = {}
    for subtag in subtags:
        subtag = subtag.strip()
        tagdict = {"Description": []}
        for line in subtag.splitlines():
            k, _, v = line.partition(": ")
            if k == "Description":
                # there could be multiple descriptions given
                tagdict["Description"].append(v)
            else:
                tagdict[k] = v
        subtag_type = tagdict.pop("Type")
        subtag_subtag = tagdict.pop("Subtag", None) or tagdict.pop("Tag")
        db.setdefault(subtag_type, {})[subtag_subtag] = tagdict
    pp = pprint.PrettyPrinter(indent=4)
    header = "# Generated from " + url + "\n# " + file_date + "\n"
    return header + "\nsubtag_database = " + pp.pformat(db)

if __name__ == '__main__':
    from sys import argv
    print(fetch_language_subtag_registry(argv[1] if (len(argv) > 1) else None))
