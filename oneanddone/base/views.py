# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.views import generic
from django.shortcuts import redirect


class HomeView(generic.TemplateView):
    template_name = 'base/home.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect('users.profile.detail')
        else:
            return super(HomeView, self).get(*args, **kwargs)
