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

from ductus.wiki.views import RegularWikiNamespace
from ductus.group.models import Group

class GroupNamespace(RegularWikiNamespace):
    def allow_edit(self, user, pagename):
        if not user.is_authenticated():
            return False

        groupname = pagename.partition('/')[0]
        try:
            group = Group.objects.get(slug=groupname)
        except Group.DoesNotExist:
            return False

        return group.users.filter(id=user.id).exists()

GroupNamespace('group')
