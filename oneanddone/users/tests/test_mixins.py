# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.exceptions import PermissionDenied

from mock import Mock, patch
from nose.tools import eq_, raises

from oneanddone.base.tests import TestCase
from oneanddone.users.mixins import BaseUserProfileRequiredMixin, PrivacyPolicyRequiredMixin, MyStaffUserRequiredMixin
from oneanddone.users.tests import UserFactory, UserProfileFactory


class FakeMixin(object):
    def dispatch(self, request, *args, **kwargs):
        return 'fakemixin'


class FakeView(BaseUserProfileRequiredMixin, FakeMixin):
    pass


class FakeViewNeedsPrivacyPolicy(PrivacyPolicyRequiredMixin, FakeMixin):
    pass


class FakeViewNeedsStaff(MyStaffUserRequiredMixin, FakeMixin):
    pass


class MyStaffUserRequiredMixinTests(TestCase):
    def setUp(self):
        self.view = FakeViewNeedsStaff()

    def test_is_staff(self):
        """
        If the user is staff, call the parent class's
        dispatch method.
        """
        request = Mock()
        request.user = UserFactory.create(is_staff=True)

        eq_(self.view.dispatch(request), 'fakemixin')

    @raises(PermissionDenied)
    def test_not_staff(self):
        """
        If the user is not staff, raise a PermissionDenied exception.
        """
        request = Mock()
        request.user = UserFactory.create(is_staff=False)
        self.view.dispatch(request)


class PrivacyPolicyRequiredMixinTests(TestCase):
    def setUp(self):
        self.view = FakeViewNeedsPrivacyPolicy()

    def test_has_profile_and_accepts_privacy_policy(self):
        """
        If the user has created a profile, and has accepted privacy policy
        call the parent class's dispatch method.
        """
        request = Mock()
        request.user = UserProfileFactory.create(privacy_policy_accepted=True).user

        eq_(self.view.dispatch(request), 'fakemixin')

    def test_has_profile_and_not_accepted_privacy_policy(self):
        """
        If the user has created a profile, and has not accepted privacy policy
        redirect them to profile update view.
        """
        request = Mock()
        request.user = UserProfileFactory.create(privacy_policy_accepted=False).user

        with patch('oneanddone.users.mixins.redirect') as redirect:
            eq_(self.view.dispatch(request), redirect.return_value)
            redirect.assert_called_with('users.profile.update')

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


class UserProfileRequiredMixinTests(TestCase):
    def setUp(self):
        self.view = FakeView()

    def test_has_profile(self):
        """
        If the user has created a profile, and has accepted privacy policy
        call the parent class's dispatch method.
        """
        request = Mock()
        request.user = UserProfileFactory.create(privacy_policy_accepted=True).user

        eq_(self.view.dispatch(request), 'fakemixin')

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
