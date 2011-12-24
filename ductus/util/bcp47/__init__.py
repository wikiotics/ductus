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

"""Utilities relating to BCP 47 (currently RFC 5646)
"""

from ductus.util.bcp47.data import subtag_database

def tag_to_description(tag):
    """Converts a bcp47 tag to a description

    Currently only supports language tags and region subtags.

    Raises KeyError if it is not found.

    >>> tag_to_description('en')
    u'English'
    >>> tag_to_description('en-us')
    u'English (United States)'
    >>> tag_to_description('EN-US')
    u'English (United States)'
    """
    subtags = tag.split('-')
    if not subtags:
        raise KeyError
    language = subtag_database['language'][subtags[0].lower()]['Description'][0]
    region = None
    if len(subtags) > 1:
        region = subtag_database['region'][subtags[1].upper()]['Description'][0]
    if len(subtags) > 2:
        raise KeyError
    rv = language
    if region:
        rv += u" (%s)" % region
    return rv
