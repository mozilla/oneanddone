# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic

from rest_framework import generics
from braces.views import LoginRequiredMixin
import django_browserid.views
from tower import ugettext as _
from random import randint
import re

from oneanddone.base.urlresolvers import reverse_lazy
from oneanddone.tasks.models import TaskAttempt
from oneanddone.users.forms import UserProfileForm, SignUpForm
from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.users.models import UserProfile
from serializers import UserSerializer


def default_username(email, counter):
    if not counter:
        random_username = re.sub(r'[\W_]+', '', email.split('@')[0])
    else:
        random_username = re.sub(r'[\W_]+', '', email.split('@')[0] + str(randint(1, 100)))

    if not UserProfile.objects.filter(username=random_username).exists():
        return random_username
    else:
        return default_username(email, counter + 1)


class CreateProfileView(generic.CreateView):
    model = UserProfile
    form_class = SignUpForm
    template_name = 'users/profile/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if (not request.user.is_authenticated() or
                UserProfile.objects.filter(user=request.user).exists()):
            return redirect('base.home')
        else:
            return super(CreateProfileView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        messages.success(self.request, _('Your profile has been created.'))
        return redirect('base.home')

    def get_initial(self):
        return {
            'username': default_username(self.request.user.email, 0),
        }


class DeleteProfileView(UserProfileRequiredMixin, generic.DeleteView):
    model = UserProfile
    success_url = reverse_lazy('base.home')
    template_name = 'users/profile/delete.html'

    def get_object(self):
        return self.request.user.profile


class LoginView(generic.TemplateView):
    template_name = 'users/login.html'


class ProfileDetailsView(generic.DetailView):
    model = UserProfile
    template_name = 'users/profile/detail.html'

    def get_context_data(self, **kwargs):
        all_attempts_finished = self.object.user.taskattempt_set.filter(state=TaskAttempt.FINISHED)
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
        context['page'] = 'ProfileDetails'
        return context

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get('username')
        if username is None:
            try:
                return self.get_queryset().get(user=self.kwargs.get('id'))
            except ObjectDoesNotExist:
                raise Http404(_(u'No UserProfiles found matching the userid'))
        try:
            return self.get_queryset().get(username=username)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404(_(u'No UserProfiles found matching the username'))


class MyProfileDetailsView(ProfileDetailsView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('base.home')
        return super(MyProfileDetailsView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.request.user.profile


class UpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    model = UserProfile
    template_name = 'users/profile/edit.html'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Your profile has been updated.'))
        return redirect('users.profile.mydetails')

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateProfileView, self).get_context_data(*args, **kwargs)
        ctx['action'] = 'Update'
        return ctx

    def get_form_class(self):
        if self.request.user.profile.privacy_policy_accepted:
            return UserProfileForm
        else:
            return SignUpForm

    def get_initial(self):
        if not self.request.user.profile.username:
            return {
                'username': default_username(self.request.user.email, 0),
            }

    def get_object(self):
        return self.request.user.profile


class Verify(django_browserid.views.Verify):
    def login_failure(self, *args, **kwargs):
        messages.error(self.request, _("""
            There was a problem signing you in. Please try again. If you continue to have issues
            logging in, let us know by emailing <a href="mailto:{email}">{email}</a>.
        """).format(email='oneanddone@mozilla.com'), extra_tags='safe')
        return super(Verify, self).login_failure(*args, **kwargs)


class UserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint used to get, update and delete user data.
    """
    lookup_field = 'email'
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListAPI(generics.ListCreateAPIView):
    """
    API endpoint used to get a complete list of users
    and create a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
