# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from rest_framework import serializers

from oneanddone.tasks.models import Task, TaskArea


class TaskAreaSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = TaskArea
        fields = ('id', 'name', 'full_name')


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'name', 'short_description', 'instructions',
                  'execution_time', 'start_date', 'end_date',
                  'is_draft', 'area')
