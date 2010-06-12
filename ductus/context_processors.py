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

from django.conf import settings
from django.utils.safestring import mark_safe

def site_settings(request):
    """Sets Ductus-specific template variables based on site settings

    Includes ductus_media_prefix, ductus_site_name, and ductus_site_head
    """
    dsn = getattr(settings, "DUCTUS_SITE_NAME", "Example Ductus Site")
    dsh = getattr(settings, "DUCTUS_SITE_HEAD", "")
    return dict(ductus_media_prefix=settings.DUCTUS_MEDIA_PREFIX,
                ductus_site_name=mark_safe(dsn),
                ductus_site_head=mark_safe(dsh),
                ductus_front_page=settings.DUCTUS_FRONT_PAGE)

def oldid(request):
    """Sets `oldid_str_amp` and `oldid_str_qm` in the context.

    One of these two variables can be safely appended to a url to make it a
    link to a given 'oldid'.  If 'oldid' is not in `request.GET`, these two
    variables will simply return the empty string.

    You should append `oldid_str_qm` to a url if is has no query_string; append
    `oldid_str_amp` if there is already a query_string that you are extending.

    See templates/ductus_document.html for examples
    """
    oldid_str_amp = oldid_str_qm = ''
    try:
        if request.GET['oldid'] and request.ductus.wiki_revision:
            oldid_str = u'oldid=%d' % request.ductus.wiki_revision.id
            oldid_str_amp = mark_safe(u'&amp;' + oldid_str)
            oldid_str_qm = mark_safe(u'?' + oldid_str)
    except (KeyError, AttributeError):
        pass
    return dict(oldid_str_amp=oldid_str_amp,
                oldid_str_qm=oldid_str_qm)

def permissions(request):
    """Sets a few variables if it's a ductus document"""
    rv = {}
    if hasattr(request, 'ductus'):
        from ductus.wiki import user_has_edit_permission
        rv['page_is_editable_by_user'] = user_has_edit_permission(request.user, request.ductus.wiki_page.name)
    return rv
