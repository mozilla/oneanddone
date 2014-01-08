# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.utils import timezone

from mock import patch
from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import Task
from oneanddone.tasks.tests import TaskAreaFactory, TaskFactory


def aware_datetime(*args, **kwargs):
    return timezone.make_aware(datetime(*args, **kwargs), timezone.utc)


class TaskAreaTests(TestCase):
    def test_full_name(self):
        root = TaskAreaFactory.create(name='root')
        child1 = TaskAreaFactory.create(parent=root, name='child1')
        child2 = TaskAreaFactory.create(parent=child1, name='child2')

        eq_(child2.full_name, 'root > child1 > child2')


class TaskTests(TestCase):
    def setUp(self):
        self.task_draft = TaskFactory.create(is_draft=True)
        self.task_no_draft = TaskFactory.create(is_draft=False)
        self.task_start_jan = TaskFactory.create(
            is_draft=False, start_date=aware_datetime(2014, 1, 1))
        self.task_end_jan = TaskFactory.create(is_draft=False, end_date=aware_datetime(2014, 1, 1))
        self.task_range_jan_feb = TaskFactory.create(
            is_draft=False, start_date=aware_datetime(2014, 1, 1),
            end_date=aware_datetime(2014, 2, 1))

    def test_isnt_available_draft(self):
        """
        If a task is marked as a draft, it should not be available.
        """
        eq_(self.task_draft.is_available, False)

    def test_isnt_available_before_start_date(self):
        """
        If the current datetime is before the start date of the task, it
        should not be available.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2013, 12, 1)
            eq_(self.task_start_jan.is_available, False)

    def test_is_available_after_start_date(self):
        """
        If the current datetime is after the start date of the task, it
        should be available.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 2, 1)
            eq_(self.task_start_jan.is_available, True)

    def test_isnt_available_after_end_date(self):
        """
        If the current datetime is after the end date of the task, it
        should not be available.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 2, 1)
            eq_(self.task_end_jan.is_available, False)

    def test_is_available_before_end_date(self):
        """
        If the current datetime is before the end date of the task, it
        should be available.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2013, 12, 1)
            eq_(self.task_end_jan.is_available, True)

    def test_is_available_within_dates(self):
        """
        If the current datetime is within the start and end date of the
        task, it should be available.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 1, 5)
            eq_(self.task_range_jan_feb.is_available, True)

    def test_is_available_filter_default_now(self):
        """
        If no timezone is given, is_available_filter should use
        timezone.now to determine the current datetime.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 1, 5)
            tasks = Task.objects.filter(Task.is_available_filter())
            expected = [self.task_no_draft, self.task_start_jan, self.task_range_jan_feb]
            eq_(set(tasks), set(expected))

    def test_is_available_filter_draft(self):
        """
        If a task is marked as a draft, it should not be available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2014, 1, 2)))
        ok_(self.task_no_draft in tasks)
        ok_(self.task_draft not in tasks)

    def test_is_available_filter_before_start_date(self):
        """
        If it is before a task's start date, the task should not be
        available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2013, 12, 1)))
        ok_(self.task_start_jan not in tasks)

    def test_is_available_filter_after_start_date(self):
        """
        If it is after a task's start date, the task should be
        available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2014, 2, 1)))
        ok_(self.task_start_jan in tasks)

    def test_is_available_filter_before_end_date(self):
        """
        If it is before a task's end date, the task should be available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2013, 12, 1)))
        ok_(self.task_end_jan in tasks)

    def test_is_available_filter_after_end_date(self):
        """
        If it is after a task's end date, the task should not be
        available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2014, 2, 1)))
        ok_(self.task_end_jan not in tasks)

    def test_is_available_filter_in_range(self):
        """
        If the current date is within a task's date range, the task
        should be available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2014, 1, 5)))
        ok_(self.task_range_jan_feb in tasks)
