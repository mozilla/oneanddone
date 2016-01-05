# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import random
import json

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from nose.tools import eq_, assert_true, assert_greater

from oneanddone.users.tests import UserFactory
from oneanddone.tasks.tests import (TaskFactory, TaskProjectFactory, TaskTeamFactory,
                                    TaskTypeFactory, TaskAttemptFactory)


class APITests(APITestCase):

    def assert_response_status(self, response, expected_status):
        eq_(response.status_code, expected_status,
            "Test Failed, got response status: %s, expected status: %s" %
            (response.status_code, expected_status))

    def create_task(self, creator):
        team = TaskTeamFactory.create()
        project = TaskProjectFactory.create()
        type = TaskTypeFactory.create()

        return TaskFactory.create(team=team, project=project, type=type,
                                  creator=creator, owner=creator)

    def setUp(self):
        self.client_user = UserFactory.create()

        # Give all permissions to the client user
        self.client_user.is_superuser = True
        self.client_user.save()

        self.token = Token.objects.create(user=self.client_user)
        self.uri = '/api/v1/task/'

    def test_client_with_false_token(self):
        """
        Test task list, task details, task deletion for user with false token
        """
        invalid_key = 'd81e33c57b2d9471f4d6849bab3cb233b3b30468'
        false_token = ''.join(random.sample(invalid_key, len(invalid_key)))

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + false_token)

        response = self.client.get(reverse('api-task'))
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

        test_task = self.create_task(self.client_user)
        task_uri = self.uri + str(test_task.id) + '/'

        get_response = self.client.get(task_uri)
        self.assert_response_status(get_response, status.HTTP_401_UNAUTHORIZED)

        delete_response = self.client.delete(task_uri)
        self.assert_response_status(delete_response, status.HTTP_401_UNAUTHORIZED)

    def test_create_new_task(self):
        """
        Test Create new task
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        team = TaskTeamFactory.create()
        project = TaskProjectFactory.create()
        type = TaskTypeFactory.create()

        task_data = {"name": "Sample Task",
                     "short_description": "Task Desc",
                     "instructions": "Task Inst",
                     "prerequisites": "Task Prerequisite",
                     "execution_time": 30,
                     "is_draft": False,
                     "is_invalid": False,
                     "project": project.name,
                     "team": team.name,
                     "type": type.name,
                     "repeatable": False,
                     "start_date": None,
                     "end_date": None,
                     "difficulty": 1,
                     "why_this_matters": "Task matters",
                     "keyword_set": [{"name": "testing"}, {"name": "mozwebqa"}],
                     "taskattempt_set": [{"user": self.client_user.email, "state": 0}],
                     "owner": self.client_user.email}

        response = self.client.post(self.uri, task_data, format='json')
        self.assert_response_status(response, status.HTTP_201_CREATED)
        response_data = json.loads(response.content)
        assert_greater(response_data['id'], 0)
        del response_data['id']
        eq_(sorted(response_data), sorted(task_data))

    def test_delete_task(self):
        """
        Test DELETE task
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        test_task = self.create_task(self.client_user)
        task_uri = self.uri + str(test_task.id) + '/'

        # Make a DELETE request
        delete_response = self.client.delete(task_uri)
        self.assert_response_status(delete_response, status.HTTP_204_NO_CONTENT)

        # Verify that the task has been deleted
        get_response = self.client.get(task_uri)
        self.assert_response_status(get_response, status.HTTP_404_NOT_FOUND)

    def test_forbidden_client(self):
        """
        Test task deletion by an authenticated but forbidden client
        """
        forbidden_user = UserFactory.create()
        forbidden_token = Token.objects.create(user=forbidden_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + forbidden_token.key)

        test_task = self.create_task(self.client_user)
        task_uri = self.uri + str(test_task.id) + '/'

        # Make a DELETE request
        delete_response = self.client.delete(task_uri)
        self.assert_response_status(delete_response, status.HTTP_403_FORBIDDEN)

    def test_get_task_details(self):
        """
        Test GET details of a task with particular id for authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user = UserFactory.create()

        test_task = self.create_task(user)
        task_attempt = TaskAttemptFactory.create(user=user, task=test_task)
        task_uri = self.uri + str(test_task.id) + '/'

        task_data = {"id": test_task.id,
                     "name": test_task.name,
                     "short_description": test_task.short_description,
                     "instructions": test_task.instructions,
                     "prerequisites": test_task.prerequisites,
                     "execution_time": test_task.execution_time,
                     "is_draft": test_task.is_draft,
                     "is_invalid": test_task.is_invalid,
                     "project": test_task.project.name,
                     "team": test_task.team.name,
                     "type": test_task.type.name,
                     "repeatable": test_task.repeatable,
                     "start_date": test_task.start_date,
                     "end_date": test_task.end_date,
                     "difficulty": test_task.difficulty,
                     "why_this_matters": test_task.why_this_matters,
                     "keyword_set": [
                         {"name": keyword.name} for keyword in test_task.keyword_set.all()],
                     "taskattempt_set": [{"user": user.email, "state": task_attempt.state}],
                     "owner": user.email}

        response = self.client.get(task_uri)
        self.assert_response_status(response, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        eq_(response_data, task_data)

    def test_get_task_list(self):
        """
        Test GET task list for authenticated user
        """
        header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token)}
        user = UserFactory.create()

        test_task = self.create_task(user)
        task_attempt = TaskAttemptFactory.create(user=user, task=test_task)
        task_data = {"id": test_task.id,
                     "name": test_task.name,
                     "short_description": test_task.short_description,
                     "instructions": test_task.instructions,
                     "prerequisites": test_task.prerequisites,
                     "execution_time": test_task.execution_time,
                     "is_draft": test_task.is_draft,
                     "is_invalid": test_task.is_invalid,
                     "project": test_task.project.name,
                     "team": test_task.team.name,
                     "type": test_task.type.name,
                     "repeatable": test_task.repeatable,
                     "start_date": test_task.start_date,
                     "end_date": test_task.end_date,
                     "difficulty": test_task.difficulty,
                     "why_this_matters": test_task.why_this_matters,
                     "keyword_set": [
                         {"name": keyword.name} for keyword in test_task.keyword_set.all()],
                     "taskattempt_set": [{"user": user.email, "state": task_attempt.state}],
                     "owner": user.email}

        response = self.client.get(reverse('api-task'), {}, **header)
        self.assert_response_status(response, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        assert_true(task_data in response_data)

    def test_unauthenticated_client(self):
        """
        Test task list, task details, task deletion for unauthenticated user
        """
        response = self.client.get(reverse('api-task'))
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

        test_task = self.create_task(self.client_user)
        task_uri = self.uri + str(test_task.id) + '/'

        get_response = self.client.get(task_uri)
        self.assert_response_status(get_response, status.HTTP_401_UNAUTHORIZED)

        delete_response = self.client.delete(task_uri)
        self.assert_response_status(delete_response, status.HTTP_401_UNAUTHORIZED)
