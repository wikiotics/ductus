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

from django.db import models
from django.contrib.auth.models import User

class WikiPage(models.Model):
    name = models.CharField(max_length=512)

    def get_absolute_url(self):
        return u'/%s/' % self.urn

    def get_latest_revision(self): # what to do if no revisions exist?
        return WikiRevision.objects.filter(page=self).order_by('-timestamp')[0]

    def __unicode__(self):
        return self.name

class WikiRevision(models.Model):
    page = models.ForeignKey(WikiPage)
    timestamp = models.DateTimeField(auto_now_add=True)
    urn = models.CharField(max_length=100) # not ideal to have a fixed max
                                           # length... is there a way we can
                                           # infer this from the urn subsystem?

    # always be sure to remove 'urn:' prefix for urn field

    author = models.ForeignKey(User, blank=True, null=True)
    author_ip = models.IPAddressField(blank=True, null=True)

    #def get_absolute_url(self):

    class Meta:
        ordering = ('-timestamp',)
        get_latest_by = 'timestamp'
        # fixme: force either username or IP to be given for a revision

    def __unicode__(self):
        return u'%s (%s)' % (unicode(self.page), self.timestamp)

# admin interface -- for debugging only

from django.contrib import admin

class WikiPageAdmin(admin.ModelAdmin):
    pass

class WikiRevisionAdmin(admin.ModelAdmin):
    pass

admin.site.register(WikiPage, WikiPageAdmin)
admin.site.register(WikiRevision, WikiRevisionAdmin)
