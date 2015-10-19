# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from rest_framework import serializers

from django.contrib.auth.models import User

from oneanddone.tasks.models import (Task, TaskAttempt, TaskKeyword,
                                     TaskProject, TaskTeam, TaskType)


class TaskAttemptSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        many=False,
        queryset=User.objects.all(),
        slug_field='email')

    class Meta:
        model = TaskAttempt
        fields = ('user', 'state')


class TaskKeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskKeyword
        fields = ('name',)


class TaskSerializer(serializers.ModelSerializer):

    taskattempt_set = TaskAttemptSerializer(
        many=True,
        read_only=True,
        required=False)
    keyword_set = TaskKeywordSerializer(
        many=True,
        read_only=True,
        required=False)
    project = serializers.SlugRelatedField(
        many=False,
        queryset=TaskProject.objects.all(),
        slug_field='name')
    team = serializers.SlugRelatedField(
        many=False,
        queryset=TaskTeam.objects.all(),
        slug_field='name')
    type = serializers.SlugRelatedField(
        many=False,
        queryset=TaskType.objects.all(),
        slug_field='name')
    owner = serializers.SlugRelatedField(
        many=False,
        queryset=User.objects.all(),
        slug_field='email')

    class Meta:
        model = Task
        fields = ('id', 'name', 'short_description', 'instructions', 'owner',
                  'prerequisites', 'execution_time', 'start_date', 'end_date',
                  'is_draft', 'is_invalid', 'project', 'team', 'type', 'repeatable',
                  'difficulty', 'why_this_matters', 'keyword_set', 'taskattempt_set')
