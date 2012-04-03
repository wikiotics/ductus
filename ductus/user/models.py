# Ductus
# Copyright (C) 2012 Laurent Savaete <laurent.savaete@gmail.com>
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
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """Profile information for each user account in ductus. See details at:
    https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    """
    user = models.OneToOneField(User, unique=True, related_name='profile')
    # the language code to use for displaying the UI
    ui_language = models.CharField(max_length=30)

def create_user_profile(sender, instance, created, **kwargs):
    """create the profile if it doesn't exist, see above for details"""
    if created:
        UserProfile.objects.create(user=instance)

# catch the django signal to create the user profile when the user is first
# saved
post_save.connect(create_user_profile, sender=User)
