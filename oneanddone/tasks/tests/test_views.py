# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.http import Http404

from mock import Mock, patch
from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks import views
from oneanddone.tasks.models import TaskAttempt
from oneanddone.tasks.tests import TaskAttemptFactory, TaskFactory
from oneanddone.users.tests import UserFactory


class TaskDetailViewTests(TestCase):
    def setUp(self):
        self.view = views.TaskDetailView()

    def test_get_context_data_not_authenticated(self):
        """
        If the current user isn't authenticated, don't include an
        attempt in the context.
        """
        self.view.request = Mock()
        self.view.request.user.is_authenticated.return_value = False

        with patch('oneanddone.tasks.views.generic.DetailView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            ok_('attempt' not in ctx)

    def test_get_context_data_authenticated(self):
        """
        If the current user is authenticated, fetch their attempt for
        the current task using get_object_or_none.
        """
        self.view.request = Mock()
        self.view.request.user.is_authenticated.return_value = True
        self.view.object = Mock()

        get_object_patch = patch('oneanddone.tasks.views.get_object_or_none')
        context_patch = patch('oneanddone.tasks.views.generic.DetailView.get_context_data')
        with get_object_patch as get_object_or_none, context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()

            eq_(ctx['attempt'], get_object_or_none.return_value)
            get_object_or_none.assert_called_with(TaskAttempt, user=self.view.request.user,
                                                  task=self.view.object, state=TaskAttempt.STARTED)


class StartTaskViewTests(TestCase):
    def setUp(self):
        self.view = views.StartTaskView()
        self.task = TaskFactory.create()
        self.view.get_object = Mock(return_value=self.task)

    def test_post_existing_attempts(self):
        """
        If the user has an existing task attempt, redirect them to the
        profile detail page.
        """
        attempt = TaskAttemptFactory.create()
        self.view.request = Mock(user=attempt.user)

        with patch('oneanddone.tasks.views.redirect') as redirect:
            eq_(self.view.post(), redirect.return_value)
            redirect.assert_called_with('users.profile.detail')
            ok_(not TaskAttempt.objects.filter(user=attempt.user, task=self.task).exists())

    def test_post_unavailable_task(self):
        """
        If the task is unavailable, redirect to the available tasks view
        without creating an attempt.
        """
        self.task.is_draft = True
        self.task.save()
        user = UserFactory.create()
        self.view.request = Mock(user=user)

        with patch('oneanddone.tasks.views.redirect') as redirect:
            eq_(self.view.post(), redirect.return_value)
            redirect.assert_called_with('tasks.available')
            ok_(not TaskAttempt.objects.filter(user=user, task=self.task).exists())

    def test_post_create_attempt(self):
        """
        If the task is available and the user doesn't have any tasks in
        progress, create a new task attempt and redirect to its page.
        """
        user = UserFactory.create()
        self.view.request = Mock(user=user)

        with patch('oneanddone.tasks.views.redirect') as redirect:
            eq_(self.view.post(), redirect.return_value)
            redirect.assert_called_with(self.task)
            ok_(TaskAttempt.objects.filter(user=user, task=self.task, state=TaskAttempt.STARTED)
                .exists())


class CreateFeedbackViewTests(TestCase):
    def setUp(self):
        self.view = views.CreateFeedbackView()

    def test_missing_attempt_404(self):
        """
        If there is no task attempt with the given ID, return a 404.
        """
        request = Mock(user=UserFactory.create())
        with self.assertRaises(Http404):
            self.view.dispatch(request, pk=9999)

    def test_feedback_not_your_attempt(self):
        """
        If the current user doesn't match the user for the requested
        task attempt, return a 404.
        """
        attempt = TaskAttemptFactory.create()
        request = Mock(user=UserFactory.create())

        with self.assertRaises(Http404):
            self.view.dispatch(request, pk=attempt.pk)
