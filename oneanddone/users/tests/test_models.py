# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import TaskAttempt
from oneanddone.tasks.tests import TaskAttemptFactory, TaskFactory
from oneanddone.users.models import User
from oneanddone.users.tests import UserFactory, UserProfileFactory


class UserTests(TestCase):
    def test_attempts_finished_count(self):
        """
        attempts_finished_count should return the number of attempts
        the user has finished.
        """
        user = UserFactory.create()
        TaskAttemptFactory.create_batch(4, user=user, state=TaskAttempt.FINISHED)
        TaskAttemptFactory.create(user=user, state=TaskAttempt.STARTED)
        eq_(user.attempts_finished_count, 4)

    def test_attempts_in_progress(self):
        """
        attempts_in_progress should return the number of attempts in progress.
        """
        user = UserFactory.create()
        tasks = TaskAttemptFactory.create_batch(4, user=user, state=TaskAttempt.STARTED)
        eq_(set(user.attempts_in_progress), set(tasks))

    def test_bugzilla_url_with_bugzilla_email(self):
        email = 'foo@example.com'
        user = UserProfileFactory.create(bugzilla_email=email)
        activity_url = 'https://bugzilla.mozilla.org/page.cgi?'\
            'id=user_activity.html&action=run&from=-14d&who=%s' % email
        eq_(user.bugzilla_url, activity_url)

    def test_bugzilla_url_with_no_bugzilla_email(self):
        user = UserProfileFactory.create()
        eq_(user.bugzilla_url, None)

    def test_display_email_with_consent(self):
        """
        The display_email attribute should return the user's email
        if they have granted consent.
        """
        user = UserProfileFactory.create(
            consent_to_email=True,
            user__email='foo@example.com').user
        eq_(user.display_email, 'foo@example.com')

    def test_display_email_without_consent(self):
        """
        The display_email attribute should return 'Email consent denied'
        if they have denied consent.
        """
        user = UserProfileFactory.create(
            consent_to_email=False,
            user__email='foo@example.com').user
        eq_(user.display_email, 'Email consent denied')

    def test_display_email_without_profile(self):
        """
        The display_email attribute should return 'Email consent denied'
        if they have no profile.
        """
        user = UserFactory.build(email='foo@example.com')
        eq_(user.display_email, 'Email consent denied')

    def test_display_name(self):
        """
        The display_name attribute should use the name from the user's
        profile.
        """
        user = UserProfileFactory.create(name='Foo Bar').user
        eq_(user.display_name, 'Foo Bar')

    def test_display_name_no_profile(self):
        """
        If the user has no profile, user.display_name should be None.
        """
        user = UserFactory.build()
        eq_(user.display_name, None)

    def test_has_completed_task_true(self):
        """
        has_completed_task should return true if the user has completed the task.
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        TaskAttemptFactory.create(user=user, task=task, state=TaskAttempt.FINISHED)
        ok_(user.has_completed_task(task))

    def test_has_completed_task_false(self):
        """
        has_completed_task should return false if the user has not completed the task.
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        ok_(not user.has_completed_task(task))

    def test_has_completed_task_false_task_abandoned(self):
        """
        has_completed_task should return false if the user has abandoned the task.
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        TaskAttemptFactory.create(user=user, task=task, state=TaskAttempt.ABANDONED)
        ok_(not user.has_completed_task(task))

    def test_has_completed_task_false_task_started(self):
        """
        has_completed_task should return false if the user has just started the task.
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        TaskAttemptFactory.create(user=user, task=task, state=TaskAttempt.STARTED)
        ok_(not user.has_completed_task(task))

    def test_profile_email_with_consent(self):
        """
        The email attribute should return the user's email
        if they have granted consent.
        """
        profile = UserProfileFactory.create(
            consent_to_email=True,
            user__email='foo@example.com')
        eq_(profile.email, 'foo@example.com')

    def test_profile_email_without_consent(self):
        """
        The email attribute should return 'Email consent denied'
        if they have denied consent.
        """
        profile = UserProfileFactory.create(
            consent_to_email=False,
            user__email='foo@example.com')
        eq_(profile.email, 'Email consent denied')

    def test_profile_url_with_username(self):
        user = UserProfileFactory.create(username='foo')
        eq_(user.profile_url, '/profile/foo/')

    def test_profile_url_with_no_username(self):
        user = UserProfileFactory.create(username=None)
        profile_url = '/profile/%s/' % user.user.id
        eq_(user.profile_url, profile_url)

    def test_unicode(self):
        """
        The string representation of a user should include their
        email address.
        """
        user = UserProfileFactory.create(name='Foo Bar', user__email='foo@example.com').user
        eq_(unicode(user), u'Foo Bar (foo@example.com)')

    def test_unicode_no_name(self):
        """
        If a user has no profile, use "Anonymous" in its place and hide the email address.
        """
        user = UserFactory.build(email='foo@example.com')
        eq_(unicode(user), u'Anonymous (Email consent denied)')

    def test_recent_users(self):
        """
        recent_users should return users sorted by most recent task activity
        """
        task = TaskFactory.create()
        user1 = UserProfileFactory.create().user
        user2 = UserProfileFactory.create().user
        user3 = UserProfileFactory.create().user
        user4 = UserFactory.create()
        TaskAttemptFactory.create(user=user4,
                                  state=TaskAttempt.STARTED,
                                  task=task)
        TaskAttemptFactory.create(user=user3,
                                  state=TaskAttempt.STARTED,
                                  task=task)
        TaskAttemptFactory.create(user=user2,
                                  state=TaskAttempt.STARTED,
                                  task=task)
        TaskAttemptFactory.create(user=user2,
                                  state=TaskAttempt.FINISHED,
                                  task=task)
        TaskAttemptFactory.create(user=user1,
                                  state=TaskAttempt.STARTED,
                                  task=task)
        TaskAttemptFactory.create(user=user3,
                                  state=TaskAttempt.ABANDONED,
                                  task=task)
        eq_(user1.taskattempt_set.all().count(), 1)
        eq_(user2.taskattempt_set.all().count(), 2)
        eq_(user3.taskattempt_set.all().count(), 2)
        eq_(user4.taskattempt_set.all().count(), 1)
        qs = User.recent_users()
        eq_(len(qs), 3)
        eq_(qs[0], user1)
        eq_(qs[1], user2)
        eq_(qs[2], user3)
