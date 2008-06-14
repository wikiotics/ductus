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

import ductus.util

class UnsupportedURN(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

__b64_chrs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
__contains_only_base64_chrs = ductus.util.sequence_contains_only(__b64_chrs)

def is_class_A_urn(urn):
    """Return True/False depending on whether the argument is a Class-A URN.

    A Class-A URN is in the format urn:hash_type:hash_digest where hash_type
    and hash_digest are nonempty and both contain only base64 characters.  This
    is an arbitrary decision made by the Ductus team.

    Some portions of the program will assume that URN's given to it are
    Class-A.  It is best always to use this function to check before assuming,
    in case the set of acceptable URN's grows in the future (in which case
    there will be a function for the newly-defined Class-B URN's.

    Class-A may become more restrictive in the future, but it will never become
    more liberal.  That's what Class-B will be for.
    """

    if not isinstance(urn, basestring):
        raise ValueError("urn must be a string")
    urn_split = urn.split(':')
    if len(urn_split) != 3:
        return False
    urn_str, hash_type, digest = urn_split
    return (urn_str == 'urn'
            and hash_type != ''
            and digest != ''
            and __contains_only_base64_chrs(hash_type)
            and __contains_only_base64_chrs(digest))

def verify_class_A_urn(urn):
    "Raise UnsupportedURN if argument is not a Class-A URN."
    if not is_class_A_urn(urn):
        raise UnsupportedURN(urn)

def verify_valid_urn(urn):
    "Raise UnsupportedURN if argument is not a valid URN in the current system"
    verify_class_A_urn(urn)
