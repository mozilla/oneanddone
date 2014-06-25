# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib.auth.models import User
from django.db import models

from tower import ugettext_lazy as _lazy

from oneanddone.tasks.models import TaskAttempt


# User class extensions
def user_unicode(self):
    """
    Change user string representation to use the user's email address.
    """
    return u'{name} <{email}>'.format(name=self.display_name or u'Anonymous', email=self.email)
User.add_to_class('__unicode__', user_unicode)


@property
def user_display_name(self):
    """
    Return this user's display name, or 'Anonymous' if they don't have a
    profile.
    """
    try:
        return self.profile.name
    except UserProfile.DoesNotExist:
        return None
User.add_to_class('display_name', user_display_name)


@property
def user_attempts_finished_count(self):
    """Number of task attempts the user has finished."""
    return self.taskattempt_set.filter(state=TaskAttempt.FINISHED).count()
User.add_to_class('attempts_finished_count', user_attempts_finished_count)


@property
def user_attempts_in_progress(self):
    """All task attempts the user has in progress."""
    return self.taskattempt_set.filter(state=TaskAttempt.STARTED)
User.add_to_class('attempts_in_progress', user_attempts_in_progress)

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    username = models.CharField(_lazy(u'Username'), max_length=30, unique=True, null=True)
    name = models.CharField(_lazy(u'Display Name:'), max_length=255)
    privacy_policy_accepted = models.BooleanField(default=False)
