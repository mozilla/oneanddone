# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.shortcuts import redirect

from oneanddone.users.models import UserProfile


class UserProfileRequiredMixin(object):
    """
    Require users to have a UserProfile before they can interact with
    the view. Must be placed after the LoginRequiredMixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not UserProfile.objects.filter(user=request.user).exists():
            return redirect('users.profile.create')
        else:
            return super(UserProfileRequiredMixin, self).dispatch(request, *args, **kwargs)
