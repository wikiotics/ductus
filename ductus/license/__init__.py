# Ductus
# Copyright (C) 2010  Jim Garrison <garrison@wikiotics.org>
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

from django.utils.translation import ugettext_lazy as _

# The information in this file should not be interpreted as legal advice.
# Consult a lawyer for any questions regarding license compatibility.

_PUBLIC_DOMAIN = 'http://creativecommons.org/licenses/publicdomain/'

_CC_BY_SA_1_0 = 'http://creativecommons.org/licenses/by-sa/1.0/'
_CC_BY_SA_2_0 = 'http://creativecommons.org/licenses/by-sa/2.0/'
_CC_BY_SA_2_5 = 'http://creativecommons.org/licenses/by-sa/2.5/'
_CC_BY_SA_3_0 = 'http://creativecommons.org/licenses/by-sa/3.0/'

_CC_BY_1_0 = 'http://creativecommons.org/licenses/by/1.0/'
_CC_BY_2_0 = 'http://creativecommons.org/licenses/by/2.0/'
_CC_BY_2_5 = 'http://creativecommons.org/licenses/by/2.5/'
_CC_BY_3_0 = 'http://creativecommons.org/licenses/by/3.0/'

license_name_map = {
    _PUBLIC_DOMAIN: _('Public Domain'),
    _CC_BY_SA_1_0: _('Creative Commons Attribution-ShareAlike 1.0'),
    _CC_BY_SA_2_0: _('Creative Commons Attribution-ShareAlike 2.0'),
    _CC_BY_SA_2_5: _('Creative Commons Attribution-ShareAlike 2.5'),
    _CC_BY_SA_3_0: _('Creative Commons Attribution-ShareAlike 3.0'),
    _CC_BY_1_0: _('Creative Commons Attribution 1.0'),
    _CC_BY_2_0: _('Creative Commons Attribution 2.0'),
    _CC_BY_2_5: _('Creative Commons Attribution 2.5'),
    _CC_BY_3_0: _('Creative Commons Attribution 3.0'),
}

__cc_by_versions = (
    _CC_BY_1_0,
    _CC_BY_2_0,
    _CC_BY_2_5,
    _CC_BY_3_0,
)

__cc_by_sa_versions = (
    _CC_BY_SA_1_0,
    _CC_BY_SA_2_0,
    _CC_BY_SA_2_5,
    _CC_BY_SA_3_0,
)

# in general, we shouldn't be relicensing something unless we have modified it
# in some way, or we are creating a new work that derives from it.  so
# everything below assumes that the destination work is a derivative work in
# some way, i.e., it is not precisely the same as the source work.

# CC License compatibility chart at http://wiki.creativecommons.org/Frequently_Asked_Questions#If_I_use_a_Creative_Commons-licensed_work_to_create_a_new_work_.28ie_a_derivative_work_or_adaptation.29.2C_which_Creative_Commons_license_can_I_use_for_my_new_work.3F

def is_license_compatible(source, dest):
    """Check license compatibility of a source and destination license

    >>> is_license_compatible('http://creativecommons.org/licenses/publicdomain/', 'http://creativecommons.org/licenses/by-sa/3.0/')
    True
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by-sa/3.0/')
    True
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/2.0/', 'http://creativecommons.org/licenses/by-sa/3.0/')
    True
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by-sa/2.0/')
    False
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by/2.0/')
    False
    >>> is_license_compatible('http://creativecommons.org/licenses/by/3.0/', 'http://creativecommons.org/licenses/by-sa/2.0/')
    True
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/3.0/', 'SOME_UNKNOWN_LICENSE')
    False
    >>> is_license_compatible('http://creativecommons.org/licenses/publicdomain/', 'SOME_UNKNOWN_LICENSE')
    True
    >>> is_license_compatible('SOME_UNKNOWN_LICENSE', 'http://creativecommons.org/licenses/by/3.0/')
    False
    >>> is_license_compatible(None, None)
    False
    >>> is_license_compatible('http://creativecommons.org/licenses/publicdomain/', None)
    True
    >>> is_license_compatible('http://creativecommons.org/licenses/by-sa/1.0/', 'http://creativecommons.org/licenses/by-sa/3.0/')
    False
    """
    if source == _PUBLIC_DOMAIN:
        return True
    if source in __cc_by_versions:
        # It seems that a work under any version of CC-BY can lead to a
        # derivative work that is licensed under /any/ version of CC-BY or
        # CC-BY-SA.  fixme: have an attorney verify that this is true
        if dest in __cc_by_versions or dest in __cc_by_sa_versions:
            return True
        else:
            return False
    # otherwise, check for some copyleft compatibility.  in our case, usually
    # this means that the target license is the same (or greater) version of
    # CC-BY-SA.
    try:
        dest_index = __cc_by_sa_versions.index(dest)
        source_index = __cc_by_sa_versions.index(source)
    except ValueError:
        # they're not both CC-BY-SA licenses.  move along.
        pass
    else:
        if source_index == 0:
            # CC-BY-SA 1.0 doesn't allow derivative works under a later version
            return bool(source_index == dest_index)
        elif dest_index >= source_index:
            return True
    return False

def is_license_compatibility_satisfied(source_list, dest_list):
    """Check license compatibility of a list of source licenses with a list of destination licenses.

    source_list is the license list for a single resource; it implies that the
    source resource is licensed under those (possibly multiple) licenses, and
    we are free to choose any one of them we wish.  if there are multiple
    resources we are deriving from, this function must be called multiple
    times, once for each source resource.  dest_list is a list of licenses we
    would like the new resource to be licensed under.

    >>> is_license_compatibility_satisfied([], [])
    False
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/publicdomain/'], [])
    True
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/publicdomain/'], ['http://creativecommons.org/licenses/publicdomain/'])
    True
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/by/3.0/'], ['http://creativecommons.org/licenses/publicdomain/'])
    False
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by/3.0/'], ['http://creativecommons.org/licenses/publicdomain/'])
    False
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by/3.0/'], [])
    False
    >>> is_license_compatibility_satisfied(['http://creativecommons.org/licenses/by/1.0/'], ['http://creativecommons.org/licenses/by-sa/3.0/', 'http://creativecommons.org/licenses/by/3.0/'])
    True
    """
    dest_list = dest_list or [None]
    for dest_license in dest_list:
        if not any(is_license_compatible(source_license, dest_license)
                   for source_license in source_list):
            return False
    return True
