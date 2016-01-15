# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import User, UserManager
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _lazy

from oneanddone.tasks.models import TaskAttempt


# User class extensions
def user_unicode(self):
    """
    Change user string representation to use the user's email address.
    """
    return u'{name} ({email})'.format(
        name=self.display_name or u'Anonymous', email=self.display_email)
User.add_to_class('__unicode__', user_unicode)


@property
def user_display_email(self):
    """
    If a user has not consented to receive emails
    return 'Email consent denied'.
    """
    no_consent_email = 'Email consent denied'
    try:
        if self.profile.consent_to_email:
            return self.email
    except UserProfile.DoesNotExist:
        return no_consent_email
    return no_consent_email
User.add_to_class('display_email', user_display_email)


@property
def user_display_name(self):
    """
    Return this user's display name, or None if they don't have a
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


@property
def user_attempts_requiring_notification(self):
    """Any task attempts that require notification."""
    return self.taskattempt_set.filter(requires_notification=True)
User.add_to_class('attempts_requiring_notification', user_attempts_requiring_notification)


@classmethod
def user_recent_users(self):
    users = User.objects.filter(
        profile__isnull=False,
        taskattempt__isnull=False,
        taskattempt__state__in=(TaskAttempt.STARTED, TaskAttempt.FINISHED)).annotate(
        activity_date=Max('taskattempt__modified')).order_by(
        '-activity_date')
    return users
User.add_to_class('recent_users', user_recent_users)


def user_has_completed_task(self, task):
    """Has the user completed the specified task?"""
    return self.taskattempt_set.filter(task=task, state=TaskAttempt.FINISHED).exists()
User.add_to_class('has_completed_task', user_has_completed_task)


class OneAndDoneUserManager(UserManager):
    # UserManager that prefetches user profiles when getting users.
    def get_queryset(self):
        return super(
            OneAndDoneUserManager, self).get_queryset().prefetch_related('profile')
        # Note: changed this from select_related to prefetch_related
        # due to https://code.djangoproject.com/ticket/15040
User.add_to_class('objects', OneAndDoneUserManager())


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')

    consent_to_email = models.BooleanField(default=True)
    name = models.CharField(_lazy(u'Display Name:'), max_length=255)
    privacy_policy_accepted = models.BooleanField(default=False)
    username = models.CharField(_lazy(u'Username'), max_length=30, unique=True, null=True)
    personal_url = models.URLField(blank=True, null=True, max_length=200)
    bugzilla_email = models.EmailField(blank=True, null=True)

    @property
    def bugzilla_url(self):
        if self.bugzilla_email:
            activity_url = 'https://bugzilla.mozilla.org/page.cgi?'\
                'id=user_activity.html&action=run&from=-14d&who=%s' % (self.bugzilla_email)
            return activity_url
        return None

    @property
    def email(self):
        return self.user.display_email

    @property
    def profile_url(self):
        if self.username is not None:
            return reverse('users.profile.details', args=[self.username])
        else:
            return reverse('users.profile.details', args=[self.user.id])

    def delete(self):
        self.user.delete()
