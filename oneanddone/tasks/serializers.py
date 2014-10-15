# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from rest_framework import serializers

from oneanddone.tasks.models import Task, TaskKeyword, TaskAttempt


class TaskAttemptSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(many=False, slug_field='email')

    class Meta:
        model = TaskAttempt
        fields = ('user', 'state')


class TaskKeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskKeyword
        fields = ('name',)


class TaskSerializer(serializers.ModelSerializer):

    taskattempt_set = TaskAttemptSerializer(required=False, many=True)
    keyword_set = TaskKeywordSerializer(required=False, many=True)
    project = serializers.SlugRelatedField(many=False, slug_field='name')
    team = serializers.SlugRelatedField(many=False, slug_field='name')
    type = serializers.SlugRelatedField(many=False, slug_field='name')
    owner = serializers.SlugRelatedField(many=False, slug_field='email')

    class Meta:
        model = Task
        fields = ('id', 'name', 'short_description', 'instructions', 'owner',
                  'prerequisites', 'execution_time', 'start_date', 'end_date',
                  'is_draft', 'is_invalid', 'project', 'team', 'type', 'repeatable',
                  'difficulty', 'why_this_matters', 'keyword_set', 'taskattempt_set')
