# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

import pytest
import requests


@pytest.fixture(scope='session')
def session_capabilities(session_capabilities):
    session_capabilities.setdefault('tags', []).append('oneanddone')
    return session_capabilities


@pytest.fixture
def persona_test_user():
    max_retries = 5
    attempt = 1
    while attempt <= max_retries:
        msg = 'There was a problem getting a personatestuser -- attempt {num}: '.format(
            num=attempt)
        try:
            response = requests.get('http://personatestuser.org/email')
            user_info = response.json()
            if user_info.get('email'):
                return user_info
        except ValueError:
            msg += 'No json was returned from personatestuser.org. \n'
            msg += 'Response status / content: {status} / {content}'.format(
                status=response.status_code,
                content=response.content)
        else:
            msg += json.dumps(user_info, indent=4, sort_keys=True)
        print msg
        attempt += 1
    raise Exception(msg)


@pytest.fixture(scope='function')
def new_user(persona_test_user):
    return {
        'email': persona_test_user['email'],
        'password': persona_test_user['pass'],
        'name': persona_test_user['email'].split('@')[0],
        'username': persona_test_user['email'].split('@')[0],
        'url': 'http://www.mozilla.org/'
    }


@pytest.fixture(scope='session')
def base_url(base_url, request):
    return base_url or request.getfuncargvalue("live_server").url


@pytest.fixture(scope='function')
def is_local(base_url):
    return '127.0.0.1' in base_url or 'localhost' in base_url


@pytest.fixture(scope='function', autouse=True)
def use_transactional_db(base_url, is_local, request):
    if is_local:
        # if we are running locally we need the transactional_db fixture
        request.getfuncargvalue("transactional_db")


@pytest.fixture(scope='function')
def task(base_url, is_local):
    if is_local:
        from oneanddone.tasks.tests import TaskFactory
        return TaskFactory.create()


@pytest.fixture(scope='function')
def assigned_task(base_url, is_local):
    if is_local:
        from oneanddone.tasks.tests import TaskFactory, TaskAttemptFactory
        from oneanddone.users.tests import UserFactory
        from oneanddone.tasks.models import TaskAttempt
        task = TaskFactory.create(repeatable=False)
        user = UserFactory.create()
        TaskAttemptFactory.create(
            user=user,
            state=TaskAttempt.STARTED,
            task=task)
        return task
    pytest.skip('Requires local instance for testing')


@pytest.fixture(scope='function')
def nonrepeatable_task(base_url, is_local):
    if is_local:
        from oneanddone.tasks.tests import TaskFactory
        return TaskFactory.create(repeatable=False)
    pytest.skip('Requires local instance for testing')
