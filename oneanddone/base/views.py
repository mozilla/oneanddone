# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.shortcuts import redirect
from django.views import generic

from oneanddone.users.models import UserProfile


class HomeView(generic.TemplateView):
    template_name = 'base/home.html'

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated() and
                not UserProfile.objects.filter(user=request.user).exists()):
            return redirect('users.profile.create')
        elif (request.user.is_authenticated() and
                not UserProfile.objects.get(user=request.user).privacy_policy_accepted):
            return redirect('users.profile.update')
        else:
            return super(HomeView, self).dispatch(request, *args, **kwargs)
