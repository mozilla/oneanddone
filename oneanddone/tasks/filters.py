# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import django_filters
from tower import ugettext_lazy as _lazy

from oneanddone.tasks.models import Task
from oneanddone.tasks.widgets import RangeInput


class TasksFilterSet(django_filters.FilterSet):
    execution_time = django_filters.NumberFilter(
        widget=RangeInput(attrs={'min': 0, 'max': 60, 'value': 60, 'step': 1}),
        label=_lazy(u'Execution time (minutes)'),
        lookup_type='lte')

    class Meta:
        model = Task
        fields = ('execution_time',)


class AvailableTasksFilterSet(TasksFilterSet):
    """
    FilterSet that finds Available Tasks based on criteria.
    """
