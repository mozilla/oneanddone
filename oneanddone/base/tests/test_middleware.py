# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.base.middleware import ClosedTaskNotificationMiddleware


class ClosedTaskNotificationMiddlewareTests(TestCase):
    def setUp(self):
        self.mw = ClosedTaskNotificationMiddleware()
        self.user = Mock()
        self.attempt = Mock()
        self.attempt.task = Mock(name='Test task name')
        self.user.attempts_requiring_notification = []
        self.request = Mock(user=self.user)

    def test_without_notification(self):
        """
        If no notification add no message and do not update attempt.
        """
        with patch('oneanddone.base.middleware.messages.warning') as warning:
            self.mw.process_request(self.request)
            ok_(not warning.called)
            ok_(not self.attempt.save.called)
            ok_(self.attempt.requires_notification is not False)

    def test_with_notification(self):
        """
        If notification then add message and update attempt.
        """
        with patch('oneanddone.base.middleware.messages.warning') as warning:
            self.request.user.attempts_requiring_notification = [self.attempt]
            self.mw.process_request(self.request)
            ok_(warning.called)
            eq_(self.attempt.requires_notification, False)
            ok_(self.attempt.save.called)
