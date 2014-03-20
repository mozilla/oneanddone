# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.users.mixins import BaseUserProfileRequiredMixin
from oneanddone.users.tests import UserFactory, UserProfileFactory


class FakeMixin(object):
    def dispatch(self, request, *args, **kwargs):
        return 'fakemixin'


class FakeView(BaseUserProfileRequiredMixin, FakeMixin):
    pass


class UserProfileRequiredMixinTests(TestCase):
    def setUp(self):
        self.view = FakeView()

    def test_no_profile(self):
        """
        If the user hasn't created a profile, redirect them to the
        profile creation view.
        """
        request = Mock()
        request.user = UserFactory.create()

        with patch('oneanddone.users.mixins.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('users.profile.create')

    def test_has_profile(self):
        """
        If the user has created a profile, call the parent class's
        dispatch method.
        """
        request = Mock()
        request.user = UserProfileFactory.create().user

        eq_(self.view.dispatch(request), 'fakemixin')
