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

from ductus.wiki import register_wiki_permission

@register_wiki_permission(u'~')
def user_permission_func(user, pagename):
    return (user.is_authenticated()
            and pagename[1:].partition('/')[0] == user.username)

from django.contrib.auth.models import User

# fix User.get_absolute_url() to point to the right place
User.get_absolute_url = lambda self: u'/wiki/~%s' % self.username
