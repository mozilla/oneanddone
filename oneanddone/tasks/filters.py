# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import operator

import django_filters
from mptt.forms import TreeNodeChoiceField

from oneanddone.tasks.models import Task, TaskArea


class TreeFilter(django_filters.Filter):
    """
    Filter that finds objects related to the given value or any of its
    descendants.
    """
    field_class = TreeNodeChoiceField

    def filter(self, queryset, value):
        key = '{name}__in'.format(name=self.name)
        return queryset.filter(**{key: value.get_descendants(include_self=True)})


class AvailableTasksFilterSet(django_filters.FilterSet):
    """
    FilterSet that finds Tasks within an area, including child areas.
    """
    execution_time = django_filters.NumberFilter(lookup_type='lte')

    class Meta:
        model = Task
        fields = ('area', 'execution_time')

    def __init__(self, *args, **kwargs):
        super(AvailableTasksFilterSet, self).__init__(*args, **kwargs)

        # Limit the area filter to TaskAreas that have available tasks.
        available_areas = TaskArea.objects.filter(Task.is_available_filter(prefix='task__')).distinct()
        ancestor_querysets = [area.get_ancestors(include_self=True) for area in available_areas]
        self.filters['area'] = TreeFilter(
            name='area',
            queryset=reduce(operator.or_, ancestor_querysets).distinct(),
            empty_label=u'All Areas'
        )
