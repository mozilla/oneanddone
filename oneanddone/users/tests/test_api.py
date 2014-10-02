# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import random
import json

from django.contrib.auth.models import Permission

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from nose.tools import eq_

from oneanddone.users.tests import UserFactory


class APITests(APITestCase):

    def assert_response_status(self, response, expected_status):
        eq_(response.status_code, expected_status,
            "Test Failed, got response status: %s, expected status: %s" %
            (response.status_code, expected_status))

    def setUp(self):
        self.client_user = UserFactory.create()

        # Add add/change/delete user permission for client
        delete_permission = Permission.objects.get(codename='delete_user')
        add_permission = Permission.objects.get(codename='add_user')
        change_permission = Permission.objects.get(codename='change_user')
        self.client_user.user_permissions.add(add_permission, change_permission,
                                              delete_permission)

        self.token = Token.objects.create(user=self.client_user)
        self.uri = '/api/v1/user/'

    def test_change_user_profile_data(self):
        """
        Test Change User Profile Data(name, username and privacy_policy_accepted)
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a new user
        user_data = {'username': 'testname', 'email': 'test@test.com',
                     'profile': {'name': 'Test Name', 'username': 'testname', 'privacy_policy_accepted': True}}
        response = self.client.post(self.uri, user_data, format='json')

        # Change Profile Data(name, username, privacy_policy_accepted)
        changed_data = {'username': 'testname', 'email': 'test@test.com',
                        'profile': {'name': 'Changed Test Name', 'username': 'testname123', 'privacy_policy_accepted': False}}
        user_uri = self.uri + user_data['email'] + '/'
        response = self.client.patch(user_uri, changed_data, format='json')

        self.assert_response_status(response, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        eq_(response_data['profile'], changed_data['profile'])

    def test_create_new_user(self):
        """
        Test Create new user with Profile Data(name, username and privacy_policy_accepted)
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        user_data = {'username': 'testuser', 'email': 'test@test.com',
                     'profile': {'name': 'Test Name', 'username': 'testuser', 'privacy_policy_accepted': True}}
        response = self.client.post(self.uri, user_data, format='json')
        self.assert_response_status(response, status.HTTP_201_CREATED)
        response_data = json.loads(response.content)
        eq_(response_data['profile'], user_data['profile'])

    def test_client_with_false_token(self):
        """
        Test user list, user details, user deletion for user with false token
        """
        invalid_key = 'd81e33c57b2d9471f4d6849bab3cb233b3b30468'
        false_token = ''.join(random.sample(invalid_key, len(invalid_key)))

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + false_token)

        response = self.client.get(reverse('api-user'))
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

        test_user = UserFactory.create()
        user_uri = self.uri + test_user.email + '/'

        get_response = self.client.get(user_uri)
        self.assert_response_status(get_response, status.HTTP_401_UNAUTHORIZED)

        delete_response = self.client.delete(user_uri)
        self.assert_response_status(delete_response, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user(self):
        """
        Test DELETE user with particular email for authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        test_user = UserFactory.create()
        user_uri = self.uri + test_user.email + '/'

        # Make a DELETE request
        delete_response = self.client.delete(user_uri)
        self.assert_response_status(delete_response, status.HTTP_204_NO_CONTENT)

        # Verify that the user has been deleted
        get_response = self.client.get(user_uri)
        self.assert_response_status(get_response, status.HTTP_404_NOT_FOUND)

    def test_forbidden_client(self):
        """
        Test user deletion by an authenticated but forbidden client
        """
        forbidden_user = UserFactory.create()
        forbidden_token = Token.objects.create(user=forbidden_user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + forbidden_token.key)

        test_user = UserFactory.create()
        user_uri = self.uri + test_user.email + '/'

        # Make a DELETE request
        delete_response = self.client.delete(user_uri)
        self.assert_response_status(delete_response, status.HTTP_403_FORBIDDEN)

    def test_get_user_details(self):
        """
        Test GET details of a user with particular email for authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        test_user = UserFactory.create()
        user_uri = self.uri + test_user.email + '/'
        response = self.client.get(user_uri)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_get_user_list(self):
        """
        Test GET user list for authenticated user
        """
        header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token)}
        response = self.client.get(reverse('api-user'), {}, **header)
        self.assert_response_status(response, status.HTTP_200_OK)

    def test_unauthenticated_client(self):
        """
        Test user list, user details, user deletion for unauthenticated user
        """
        response = self.client.get(reverse('api-user'))
        self.assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

        test_user = UserFactory.create()
        user_uri = self.uri + test_user.email + '/'

        get_response = self.client.get(user_uri)
        self.assert_response_status(get_response, status.HTTP_401_UNAUTHORIZED)

        delete_response = self.client.delete(user_uri)
        self.assert_response_status(delete_response, status.HTTP_401_UNAUTHORIZED)
