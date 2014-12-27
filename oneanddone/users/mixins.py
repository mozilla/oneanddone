# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from braces.views import LoginRequiredMixin

from oneanddone.users.models import UserProfile


class BaseUserProfileRequiredMixin(object):
    """
    Require users to have a UserProfile before they can interact with
    the view.
    """
    def dispatch(self, request, *args, **kwargs):
        if not UserProfile.objects.filter(user=request.user).exists():
            return redirect('users.profile.create')
        else:
            return super(BaseUserProfileRequiredMixin, self).dispatch(request, *args, **kwargs)


class MyStaffUserRequiredMixin(object):
    """
    Require a user to be staff before they can interact with the view.
    Throw an exception if they are not.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super(MyStaffUserRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class UserProfileRequiredMixin(LoginRequiredMixin, BaseUserProfileRequiredMixin):
    """
    Require a user to be both logged in and have a UserProfile before
    they can interact with the view.
    """
