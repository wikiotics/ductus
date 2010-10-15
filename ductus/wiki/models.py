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
from django.core import exceptions
from django.utils.encoding import iri_to_uri
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.http import urlquote

from ductus.wiki import get_resource_database
from ductus.wiki.namespaces import split_pagename

class WikiPage(models.Model):
    name = models.CharField(max_length=512)

    def get_absolute_url(self):
        slashname = u'/'.join(self.name.split(u':', 1))
        return u'/%s' % iri_to_uri(urlquote(slashname))

    def get_latest_revision(self):
        # fixme: we need a db_index on page/timestamp combo
        query = WikiRevision.objects.filter(page=self).order_by('-timestamp')
        try:
            return query[0]
        except IndexError:
            return None

    def __unicode__(self):
        return self.name

    def split_pagename(self):
        return split_pagename(self.name)

class WikiRevision(models.Model):
    page = models.ForeignKey(WikiPage)
    timestamp = models.DateTimeField(auto_now_add=True)
    urn = models.CharField(max_length=100, blank=True)

        # always be sure to remove 'urn:' prefix when reading or setting urn
        # field

        # not ideal to have a fixed max length... is there a way we can infer
        # this from the urn subsystem?

        # blank "urn" means the page has been unlinked (i.e. "deleted")

    author = models.ForeignKey(User, blank=True, null=True)
    author_ip = models.IPAddressField(blank=True, null=True)
    log_message = models.CharField(max_length=400, blank=True)

    class Meta:
        ordering = ('-timestamp',)
        get_latest_by = 'timestamp'

    def save(self, *args, **kwargs):
        # fixme: See Django #6845.  We may need to move these tests to a
        # special validation function some day.
        assert not self.urn.startswith('urn:')
        if self.urn and ('urn:%s' % self.urn) not in get_resource_database():
            raise exceptions.ValidationError(_("urn is not in database: urn:%s") % self.urn)
        if (not self.author) and (not self.author_ip):
            raise exceptions.ValidationError(_("A user or IP address must be given when saving a revision"))
        return super(WikiRevision, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if not self.urn:
            return None
        return u'%s?oldid=%d' % (self.page.get_absolute_url(), self.id)

    def __unicode__(self):
        return u'%s (%s)' % (unicode(self.page), self.timestamp)
