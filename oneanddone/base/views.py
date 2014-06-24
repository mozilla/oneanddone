# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.shortcuts import redirect
from django.views import generic
from django_filters.views import FilterView

from oneanddone.tasks.filters import AvailableTasksFilterSet
from oneanddone.tasks.models import Task
from oneanddone.tasks.mixins import TaskMustBePublishedMixin
from oneanddone.users.models import UserProfile

class HomeView(TaskMustBePublishedMixin, FilterView):
    template_name = 'base/home.html'
    # filter so only easy ones shown
    queryset = Task.objects.filter(difficulty=1).order_by('-execution_time')
    context_object_name = 'tasks'
    paginate_by = 10
    filterset_class = AvailableTasksFilterSet

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated() and
                not UserProfile.objects.filter(user=request.user).exists()):
            return redirect('users.profile.create')
        else:
            return super(HomeView, self).dispatch(request, *args, **kwargs)
