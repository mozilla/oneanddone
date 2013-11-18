# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
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


class AreaChoiceField(TreeNodeChoiceField):
    def label_from_instance(self, area):
        return area.name


class AreaFilter(TreeFilter):
    field_class = AreaChoiceField


class AvailableTasksFilterSet(django_filters.FilterSet):
    """
    FilterSet that finds Tasks within an area, including child areas.
    """
    area = TreeFilter(name='area', queryset=TaskArea.objects.all())
    execution_time = django_filters.NumberFilter(lookup_type='lte')

    class Meta:
        model = Task
        fields = ('area', 'execution_time')
