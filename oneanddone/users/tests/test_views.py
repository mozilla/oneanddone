# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.users import views
from oneanddone.users.tests import UserFactory, UserProfileFactory


class CreateProfileViewTests(TestCase):
    def setUp(self):
        self.view = views.CreateProfileView()

    def test_dispatch_existing_profile(self):
        """
        If the user already has a profile, redirect them to the profile
        detail page.
        """
        request = Mock()
        request.user = UserProfileFactory.create().user

        with patch('oneanddone.users.views.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('users.profile.detail')

    def test_dispatch_no_profile(self):
        """If the user has no profile, dispatch the request normally."""
        request = Mock()
        request.user = UserFactory.create()

        with patch('oneanddone.users.views.generic.CreateView.dispatch') as dispatch:
            eq_(self.view.dispatch(request), dispatch.return_value)
            dispatch.assert_called_with(request)
