# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import TaskAttempt
from oneanddone.tasks.tests import TaskAttemptFactory
from oneanddone.users.tests import UserFactory, UserProfileFactory


class UserTests(TestCase):
    def test_unicode(self):
        """
        The string representation of a user should include their
        email address.
        """
        user = UserProfileFactory.create(name='Foo Bar', user__email='foo@example.com').user
        eq_(unicode(user), u'Foo Bar <foo@example.com>')

    def test_unicode_no_name(self):
        """
        If a user has no display name, use "Anonymous" in its place.
        """
        user = UserFactory.build(email='foo@example.com')
        eq_(unicode(user), u'Anonymous <foo@example.com>')

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

    def test_attempts_finished_count(self):
        user = UserFactory.create()
        TaskAttemptFactory.create_batch(4, user=user, state=TaskAttempt.FINISHED)
        TaskAttemptFactory.create(user=user, state=TaskAttempt.STARTED)
        eq_(user.attempts_finished_count, 4)

    def test_attempts_in_progress(self):
        user = UserFactory.create()
        tasks = TaskAttemptFactory.create_batch(4, user=user, state=TaskAttempt.STARTED)
        eq_(set(user.attempts_in_progress), set(tasks))
