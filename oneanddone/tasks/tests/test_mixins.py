# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_

from django.http import Http404

from oneanddone.base.tests import TestCase
from oneanddone.tasks import mixins
from oneanddone.tasks.models import TaskAttempt
from oneanddone.tasks.tests import FeedbackFactory, TaskAttemptFactory
from oneanddone.users.tests import UserFactory


class GetUserAttemptForFeedbackTests(TestCase):
    def setUp(self):
        self.view = self.make_view()

    def make_view(self):
        """
        Create a fake view that applies the mixin to the dispatch method.
        """
        class BaseView(object):
            def dispatch(self, request, *args, **kwargs):
                pass

        class View(mixins.GetUserAttemptForFeedbackMixin, BaseView):
            pass

        return View()

    def test_found_attempt_stores_attempt(self):
        """
        If the current user has a matching attempt, it should
        be stored in the view.
        """
        user = UserFactory.create()
        attempt = TaskAttemptFactory.create(user=user, state=TaskAttempt.FINISHED)
        request = Mock(user=user)

        self.view.dispatch(request, pk=attempt.pk)
        eq_(self.view.attempt, attempt)

    def test_missing_attempt_raises_404(self):
        """
        If there is no task attempt with the given ID, return a 404.
        """
        request = Mock(user=UserFactory.create())
        with self.assertRaises(Http404):
            self.view.dispatch(request, pk=9999)

    def test_not_your_attempt_raises_404(self):
        """
        If the current user doesn't match the user for the requested
        task attempt, return a 404.
        """
        attempt = TaskAttemptFactory.create()
        request = Mock(user=UserFactory.create())

        with self.assertRaises(Http404):
            self.view.dispatch(request, pk=attempt.pk)

    def test_attempt_with_feedback_raises_404(self):
        """
        If the current user has an attempt but feedback has already been
        provided, return a 404.
        """
        user = UserFactory.create()
        attempt = TaskAttemptFactory.create(user=user, state=TaskAttempt.FINISHED)
        FeedbackFactory.create(attempt=attempt)
        request = Mock(user=UserFactory.create())

        with self.assertRaises(Http404):
            self.view.dispatch(request, pk=attempt.pk)


class TaskMustBeAvailableMixinTests(TestCase):
    def make_view(self, queryset, allow_expired_tasks_attr):
        """
        Create a fake view that applies the mixin to the given queryset
        when get_queryset is called.
        """
        class BaseView(object):
            def get_queryset(self):
                return queryset

        class View(mixins.TaskMustBeAvailableMixin, BaseView):
            allow_expired_tasks = allow_expired_tasks_attr

        return View()

    def test_get_queryset(self):
        """
        get_queryset should filter the parent class' queryset with the
        availability filter from Task.
        """
        queryset = Mock()
        view = self.make_view(queryset, False)

        with patch('oneanddone.tasks.mixins.Task') as Task:
            eq_(view.get_queryset(), queryset.filter.return_value)
            queryset.filter.assert_called_with(Task.is_available_filter.return_value)
            Task.is_available_filter.assert_called_with(allow_expired=False)
