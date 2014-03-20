# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock, patch
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks import mixins


class TaskMustBePublishedMixinTests(TestCase):
    def make_view(self, queryset, allow_expired_tasks_attr):
        """
        Create a fake view that applies the mixin to the given queryset
        when get_queryset is called.
        """
        class BaseView(object):
            def get_queryset(self):
                return queryset

        class View(mixins.TaskMustBePublishedMixin, BaseView):
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
