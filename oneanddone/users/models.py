# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib.auth.models import User
from django.db import models

from tower import ugettext_lazy as _lazy


# User class extensions
def user_unicode(self):
    """Change user string representation to use the user's email address."""
    return u'{name} <{email}>'.format(self.display_name or 'Anonymous', self.email)
User.add_to_class('__unicode__', user_unicode)


@property
def user_display_name(self):
    """Return this user's display name, or 'Anonymous' if they don't have a profile."""
    try:
        return self.profile.name
    except UserProfile.DoesNotExist:
        return None
User.add_to_class('display_name', user_display_name)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    name = models.CharField(_lazy(u'Name'), max_length=255)
