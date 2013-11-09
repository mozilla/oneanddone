# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.shortcuts import redirect
from django.views import generic

from braces.views import LoginRequiredMixin
from funfactory.urlresolvers import reverse_lazy

from oneanddone.users.forms import UserProfileForm
from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.users.models import UserProfile


class CreateProfileView(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('users.profile.detail')
        else:
            return super(CreateProfileView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return redirect('users.profile.detail')


class UpdateProfileView(LoginRequiredMixin, UserProfileRequiredMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'
    success_url = reverse_lazy('users.profile.detail')

    def get_object(self):
        return self.request.user.profile


class ProfileDetailView(LoginRequiredMixin, UserProfileRequiredMixin, generic.DetailView):
    model = UserProfile
    template_name = 'users/profile/detail.html'

    def get_object(self):
        return self.request.user.profile
