# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.test.utils import override_settings

from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import TaskAttempt
from oneanddone.tasks.tests import TaskAttemptFactory, TaskFactory, ValidTaskAttemptFactory
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

    @override_settings(MIN_DURATION_FOR_COMPLETED_ATTEMPTS=10)
    def test_users_with_valid_completed_attempt_counts(self):
        """
        users_with_valid_completed_attempt_counts should return counts of all attempts completed
        within the time threshold, sorted by highest number of attempts
        """
        task = TaskFactory.create()
        user1 = UserFactory.create()
        user2 = UserFactory.create()
        # Invalid attempt
        TaskAttemptFactory.create(user=user1,
                                  state=TaskAttempt.FINISHED,
                                  task=task)
        # Valid attempts
        ValidTaskAttemptFactory.create_batch(2,
                                             user=user1,
                                             state=TaskAttempt.FINISHED,
                                             task=task)
        ValidTaskAttemptFactory.create(user=user2,
                                       state=TaskAttempt.FINISHED,
                                       task=task)
        ValidTaskAttemptFactory.create(user=user1,
                                       state=TaskAttempt.STARTED,
                                       task=task)
        eq_(user1.taskattempt_set.filter(state=TaskAttempt.STARTED).count(), 1)
        eq_(user1.taskattempt_set.filter(state=TaskAttempt.FINISHED).count(), 3)
        eq_(user2.taskattempt_set.filter(state=TaskAttempt.FINISHED).count(), 1)
        qs = User.users_with_valid_completed_attempt_counts()
        eq_(len(qs), 2)
        eq_(qs[0], user1)
        eq_(qs[0].valid_completed_attempts_count, 2)
        eq_(qs[1], user2)
        eq_(qs[1].valid_completed_attempts_count, 1)
