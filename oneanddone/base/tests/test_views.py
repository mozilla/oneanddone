# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.views import HomeView
from oneanddone.users.tests import UserFactory


class HomeViewTests(TestCase):
    def setUp(self):
        self.view = HomeView()
        self.view.request = Mock()

    def test_get_unauthenticated_super(self):
        """
        If the current user isn't authenticated, call the parent method.
        """
        self.view.request.user.is_authenticated.return_value = False

        with patch('oneanddone.base.views.HomeView.get') as parent_get:
            eq_(self.view.get('baz', foo='bar'), parent_get.return_value)
            parent_get.assert_called_with('baz', foo='bar')

    def test_dispatch_authenticated_without_profile(self):
        """
        If the user is authenticated but doesn't have a profile,
        redirect them to the create profile page.
        """
        request = Mock()
        request.user = UserFactory.create()
        request.user.is_authenticated = Mock(return_value=True)

        with patch('oneanddone.base.views.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('users.profile.create')
