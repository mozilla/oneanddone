# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms

import django_filters
from tower import ugettext_lazy as _lazy

from oneanddone.base.filters import MultiFieldFilter
from oneanddone.tasks.models import Task, TaskTeam, TaskProject, TaskType
from oneanddone.tasks.widgets import HorizCheckboxSelect


class TasksFilterSet(django_filters.FilterSet):
    search = MultiFieldFilter(
        ['name', 'short_description', 'why_this_matters',
         'prerequisites', 'instructions', 'keyword_set__name'],
        label=_lazy(u'Search for tasks')
    )

    execution_time = django_filters.MultipleChoiceFilter(
        choices=((15, 15), (30, 30), (45, 45), (60, 60)),
        widget=HorizCheckboxSelect,
        label=_lazy(u'Estimated minutes'))

    team = django_filters.ModelMultipleChoiceFilter(
        label=_lazy(u'Team'),
        queryset=TaskTeam.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    project = django_filters.ModelMultipleChoiceFilter(
        label=_lazy(u'Project'),
        queryset=TaskProject.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    type = django_filters.ModelMultipleChoiceFilter(
        label=_lazy(u'Type'),
        queryset=TaskType.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    keyword = django_filters.CharFilter(
        name='keyword_set__name'
    )

    class Meta:
        model = Task
        fields = ('search', 'execution_time', 'team', 'project', 'type', 'keyword')
