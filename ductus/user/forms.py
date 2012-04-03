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

from django import forms
from django.contrib.auth.models import User
from ductus.user.models import UserProfile
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.utils.translation import ugettext_lazy

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        # add email address as a shown field
        model = User
        fields = ("username", "password1", "password2", "email")

# make DEK happy http://www-cs-faculty.stanford.edu/~uno/email.html
UserEditForm.base_fields["email"].label = ugettext_lazy("Email address")
UserCreationForm.base_fields["email"].label = ugettext_lazy("Email address")

UserCreationForm.base_fields["email"].help_text = ugettext_lazy("Providing an email address is completely optional.")
