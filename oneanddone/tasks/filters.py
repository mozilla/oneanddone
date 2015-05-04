# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django import forms
from django.contrib.auth.models import User

import django_filters
from tower import ugettext_lazy as _lazy

from oneanddone.base.filters import MultiFieldFilter, MyDateRangeFilter
from oneanddone.tasks.models import Task, TaskAttempt, TaskProject, TaskTeam, TaskType
from oneanddone.base.widgets import HorizCheckboxSelect


class ActivityFilterSet(django_filters.FilterSet):

    task__owner = django_filters.ModelChoiceFilter(
        label=_lazy(u'Task Owner'),
        queryset=User.objects.filter(is_staff=True).order_by('profile__name'))

    task__team = django_filters.ModelChoiceFilter(
        label=_lazy(u'Team'),
        queryset=TaskTeam.objects.all())

    user = MultiFieldFilter(
        ['user__profile__name', 'user__profile__username', 'user__email'],
        label=_lazy(u'Task User')
    )

    modified = MyDateRangeFilter(
        label=_lazy(u'Date')
    )

    class Meta:
        model = TaskAttempt
        fields = ('task__owner', 'task__team', 'user', 'modified')


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
