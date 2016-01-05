# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from uuid import uuid4

from django.http import Http404

from mock import Mock, patch, PropertyMock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.urlresolvers import reverse_lazy
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


class MyProfileDetailsViewTests(TestCase):
    def setUp(self):
        self.view = views.MyProfileDetailsView()
        self.request = Mock()

    def test_dispatch_not_logged_in(self):
        """
        If the user is not logged in,
        redirect them to the home page.
        """
        user = Mock()
        user.is_authenticated.return_value = False
        self.request.user = user

        with patch('oneanddone.users.views.redirect') as redirect:
            eq_(self.view.dispatch(self.request), redirect.return_value)
            redirect.assert_called_with('base.home')

    def test_get_object(self):
        """
        Return the current user's profile.
        """
        self.request.user = UserProfileFactory.create().user
        self.view.request = self.request
        eq_(self.view.get_object(), self.request.user.profile)


class ProfileDetailsViewTests(TestCase):
    def setUp(self):
        self.view = views.ProfileDetailsView()
        self.view.kwargs = {}
        self.request = Mock()

    def test_get_object_existing_userid(self):
        """
        If a userid is passed in ,return that user's profile.
        """
        user = UserProfileFactory.create().user
        self.view.kwargs['username'] = None
        self.view.kwargs['id'] = user.id
        eq_(self.view.get_object(), user.profile)

    def test_get_object_existing_username(self):
        """
        If an existing username is passed in, return that user's profile.
        """
        user = UserProfileFactory.create().user
        self.view.kwargs['username'] = user.profile.username

        eq_(self.view.get_object(), user.profile)

    def test_get_object_non_existent_username(self):
        """
        If a non-existent username is passed in, throw a 404.
        """
        user = UserProfileFactory.create().user
        self.view.kwargs['username'] = user.profile.username + str(datetime.today())

        with self.assertRaises(Http404):
            self.view.get_object()


class VerifyViewTests(TestCase):

    def setUp(self):
        self.view = views.Verify()

    def test_success_url_no_profile(self):
        """
        If the user has no profile, return the url to create user profile.
        """
        user = UserFactory.create()
        self.view.user = user
        eq_(self.view.success_url, reverse_lazy('users.profile.create'))

    def test_success_url_no_privacy_policy(self):
        """
        If the user has not accepted the privacy policy,
        return the url to edit user profile.
        """
        profile = UserProfileFactory.create(privacy_policy_accepted=False)
        self.view.user = profile.user
        eq_(self.view.success_url, reverse_lazy('users.profile.update'))

    def test_success_url_user_ok(self):
        """
        If the user has a profile and has accepted the privacy policy,
        return the parent success_url.
        """
        profile = UserProfileFactory.create(privacy_policy_accepted=True)
        self.view.user = profile.user
        success_url_patch = patch('django_browserid.views.Verify.success_url',
                                  new_callable=PropertyMock)
        with success_url_patch as parent_success_url:
            parent_success_url.return_value = str(uuid4())
            eq_(self.view.success_url, parent_success_url.return_value)
            parent_success_url.assert_called_once_with()
