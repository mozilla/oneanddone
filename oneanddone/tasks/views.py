# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.db.models import Q
from django.utils import timezone
from django.views import generic

from django_filters.views import FilterView

from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.tasks.filters import AvailableTasksFilterSet
from oneanddone.tasks.models import Task, TaskAttempt


class AvailableTasksView(UserProfileRequiredMixin, FilterView):
    context_object_name = 'available_tasks'
    template_name = 'tasks/available.html'
    paginate_by = 10
    filterset_class = AvailableTasksFilterSet

    def get_queryset(self):
        now = timezone.now()

        # Only filter by dates if they are not null.
        start_filter = Q(start_date__isnull=True) | Q(start_date__gt=now)
        end_filter = Q(end_date__isnull=True) | Q(end_date__gt=now)

        # Exclude finished tasks, unless they allow multiple finishes.
        finished_filter = (Q(allow_multiple_finishes=True) |
                           ~Q(taskattempt__state=TaskAttempt.FINISHED))

        return (Task.objects
                .filter(start_filter, end_filter, finished_filter)
                .order_by('-execution_time'))


class TaskDetailView(UserProfileRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'tasks/detail.html'
