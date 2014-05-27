# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import generics, permissions
import django_browserid.views
from funfactory.urlresolvers import reverse_lazy
from tower import ugettext as _

from oneanddone.tasks.models import TaskAttempt
from oneanddone.users.forms import UserProfileForm
from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.users.models import UserProfile
from serializers import UserSerializer, UserProfileSerializer


class LoginView(generic.TemplateView):
    template_name = 'users/login.html'


class Verify(django_browserid.views.Verify):
    def login_failure(self, *args, **kwargs):
        messages.error(self.request, _("""
            There was a problem signing you in. Please try again. If you continue to have issues
            logging in, let us know by emailing <a href="mailto:{email}">{email}</a>.
        """).format(email='oneanddone@mozilla.com'), extra_tags='safe')
        return super(Verify, self).login_failure(*args, **kwargs)


class CreateProfileView(generic.CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('base.home')
        else:
            return super(CreateProfileView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return redirect('base.home')


class UpdateProfileView(UserProfileRequiredMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'
    success_url = reverse_lazy('base.home')

    def get_object(self):
        return self.request.user.profile

class ProfileDetailsView(UserProfileRequiredMixin, generic.DetailView):
    model = UserProfile
    template_name = 'users/profile/detail.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        all_attempts_finished = self.request.user.taskattempt_set.filter(state=TaskAttempt.FINISHED)
        paginator = Paginator(all_attempts_finished, 20)
        page = self.request.GET.get('page', 1)

        try:
            attempts_finished = paginator.page(page)
        except PageNotAnInteger:
            attempts_finished = paginator.page(1)
        except EmptyPage:
            attempts_finished = paginator.page(paginator.num_pages)

        context = super(ProfileDetailsView, self).get_context_data(**kwargs)
        context['attempts_finished'] = attempts_finished
        return context


class UserListAPI(generics.ListCreateAPIView):
    """
    API endpoint used to get a complete list of users
    and create a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint used to get, update and delete user data.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'
