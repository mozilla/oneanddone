# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.urlresolvers import reverse
from django.http import Http404

from mock import Mock, patch
from nose.tools import eq_, ok_
from tower import ugettext as _

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
        self.view.object = Mock()

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

    def test_get_context_data_taken_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request = Mock()
        self.view.request.user.is_authenticated.return_value = False
        self.view.object = Mock()
        self.view.object.is_taken = True

        with patch('oneanddone.tasks.views.generic.DetailView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Taken'))
            eq_(ctx['gs_button_disabled'], True)

    def test_get_context_data_completed_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request = Mock()
        self.view.request.user.is_authenticated.return_value = False
        self.view.object = Mock()
        self.view.object.is_taken = False
        self.view.object.is_completed = True

        with patch('oneanddone.tasks.views.generic.DetailView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Completed'))
            eq_(ctx['gs_button_disabled'], True)

    def test_get_context_data_available_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request = Mock()
        self.view.request.user.is_authenticated.return_value = False
        self.view.object = Mock()
        self.view.object.is_taken = False
        self.view.object.is_completed = False

        with patch('oneanddone.tasks.views.generic.DetailView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Get Started'))
            eq_(ctx['gs_button_disabled'], False)


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
            redirect.assert_called_with('base.home')
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


class RandomTasksViewTests(TestCase):
    def setUp(self):
        self.view = views.RandomTasksView()

    def test_get_context_data_returns_slice(self):
        """
        A subset of 5 items should be returned when Random tasks are viewed.
        """
        with patch('oneanddone.tasks.views.generic.ListView.get_context_data') as get_context_data:
            get_context_data.return_value = {'object_list': [i for i in range(0, 10)]}
            ctx = self.view.get_context_data()
            eq_(len(ctx['random_task_list']), 5)


class CreateTaskViewTests(TestCase):
    def setUp(self):
        self.view = views.CreateTaskView()

    def test_get_context_data_returns_add_action_and_url(self):
        """
        The 'Add' action and correct cancel_url
        should be included in the context data.
        """
        with patch('oneanddone.tasks.views.generic.CreateView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['action'], 'Add')
            eq_(ctx['cancel_url'], reverse('tasks.list'))


class UpdateTaskViewTests(TestCase):
    def setUp(self):
        self.view = views.UpdateTaskView()

    def test_get_context_data_returns_update_action_and_url(self):
        """
        The 'Update' action and correct cancel_url
        should be included in the context data.
        """
        get_object_patch = patch('oneanddone.tasks.views.generic.UpdateView.get_object')
        context_patch = patch('oneanddone.tasks.views.generic.UpdateView.get_context_data')
        with get_object_patch as get_object, context_patch as get_context_data:
            get_object.return_value = Mock(id=1)
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['action'], 'Update')
            eq_(ctx['cancel_url'], reverse('tasks.detail', args=[1]))
