# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.shortcuts import redirect
from django_filters.views import FilterView

from tower import ugettext as _

from oneanddone.tasks.filters import TasksFilterSet
from oneanddone.tasks.models import Task, TaskTeam
from oneanddone.tasks.mixins import TaskMustBeAvailableMixin
from oneanddone.users.models import UserProfile


class HomeView(TaskMustBeAvailableMixin, FilterView):
    template_name = 'base/home.html'
    queryset = Task.objects.filter(difficulty=Task.BEGINNER)
    context_object_name = 'tasks'
    paginate_by = 10
    filterset_class = TasksFilterSet

    def get_context_data(self, *args, **kwargs):
        ctx = super(HomeView, self).get_context_data(*args, **kwargs)
        ctx['task_list_heading'] = _('Suggested First Tasks')
        ctx['teams'] = TaskTeam.objects.all()
        return ctx

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated() and
                not UserProfile.objects.filter(user=request.user).exists()):
            return redirect('users.profile.create')
        elif (request.user.is_authenticated() and
                not UserProfile.objects.get(user=request.user).privacy_policy_accepted):
            return redirect('users.profile.update')
        else:
            return super(HomeView, self).dispatch(request, *args, **kwargs)
