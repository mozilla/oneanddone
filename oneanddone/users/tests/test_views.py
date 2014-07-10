# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.http import Http404

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
        If the user already has a profile, redirect them to the home page.
        """
        request = Mock()
        request.user = UserProfileFactory.create().user

        with patch('oneanddone.users.views.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('base.home')

    def test_dispatch_no_profile(self):
        """
        If the user has no profile, dispatch the request normally.
        """
        request = Mock()
        request.user = UserFactory.create()

        with patch('oneanddone.users.views.generic.CreateView.dispatch') as dispatch:
            eq_(self.view.dispatch(request), dispatch.return_value)
            dispatch.assert_called_with(request)

    def test_dispatch_not_logged_in(self):
        """
        If the user is not logged in, redirect them to the home page.
        """
        user = Mock()
        user.is_authenticated.return_value = False
        request = Mock(user=user)

        with patch('oneanddone.users.views.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('base.home')


class ProfileDetailsViewTests(TestCase):
    def setUp(self):
        self.view = views.ProfileDetailsView()
        self.request = Mock()

    def test_dispatch_not_logged_in_no_username(self):
        """
        If the user is not logged in and does not provide a username on the url,
        redirect them to the home page.
        """
        user = Mock()
        user.is_authenticated.return_value = False
        self.request.user = user

        with patch('oneanddone.users.views.redirect') as redirect:
            eq_(self.view.dispatch(self.request), redirect.return_value)
            redirect.assert_called_with('base.home')

    def test_get_object_existing_username(self):
        """
        If an existing username is passed in, return that user's profile.
        """
        user = UserProfileFactory.create().user

        eq_(self.view.get_object(self.request, username=user.profile.username), user.profile)

    def test_get_object_non_existent_username(self):
        """
        If a non-existent username is passed in, throw a 404.
        """
        user = UserProfileFactory.create().user
        bad_username = user.profile.username + str(datetime.today())

        with self.assertRaises(Http404):
            self.view.get_object(self.request, username=bad_username)

    def test_get_object_no_username(self):
        """
        If no username is passed in, return the current user's profile.
        """
        self.request.user = UserProfileFactory.create().user
        eq_(self.view.get_object(self.request), self.request.user.profile)
