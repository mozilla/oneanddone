# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.utils import timezone

from mock import patch
from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import Task, TaskKeyword, TaskAttempt
from oneanddone.tasks.tests import TaskFactory, TaskKeywordFactory, TaskAttemptFactory
from oneanddone.users.tests import UserFactory


def aware_datetime(*args, **kwargs):
    return timezone.make_aware(datetime(*args, **kwargs), timezone.utc)


class TaskTests(TestCase):
    def setUp(self):
        user = UserFactory.create()
        self.task_not_repeatable_no_attempts = TaskFactory.create(repeatable=False)
        self.task_not_repeatable_abandoned_attempt = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(
            user=user,
            state=TaskAttempt.ABANDONED,
            task=self.task_not_repeatable_abandoned_attempt)
        self.task_not_repeatable_started_attempt = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(
            user=user,
            state=TaskAttempt.STARTED,
            task=self.task_not_repeatable_started_attempt)
        self.task_not_repeatable_finished_attempt = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(
            user=user,
            state=TaskAttempt.FINISHED,
            task=self.task_not_repeatable_finished_attempt)
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
        This also tests the repeatable aspect of the filter by
        ensuring that tasks with attempts that are started or
        finished are not included, but those with no attempts
        or abandoned attempts are included.
        """
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 1, 5)
            tasks = Task.objects.filter(Task.is_available_filter())
            expected = [self.task_not_repeatable_no_attempts,
                        self.task_not_repeatable_abandoned_attempt,
                        self.task_no_draft, self.task_start_jan,
                        self.task_range_jan_feb]
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

    def test_keywords_list_returns_expected_string(self):
        """
        keywords_list should return a comma delimited list of keywords.
        """
        TaskKeywordFactory.create_batch(4, task=self.task_draft)
        keywords = TaskKeyword.objects.filter(task=self.task_draft)
        expected_keywords = ', '.join([keyword.name for keyword in keywords])
        eq_(self.task_draft.keywords_list, expected_keywords)

    def test_is_available_to_user_no_attempts(self):
        """
        If there are no attempts,
        the task should be available.
        """
        user = UserFactory.create()
        eq_(self.task_not_repeatable_no_attempts.is_available_to_user(user), True)

    def test_is_available_to_user_user_attempt(self):
        """
        If there is an attempt by the current user,
        the task should be available.
        """
        user = UserFactory.create()
        task = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(user=user, state=TaskAttempt.STARTED, task=task)
        eq_(task.is_available_to_user(user), True)

    def test_is_available_to_user_other_user_abandoned_attempt(self):
        """
        If there is a non-abandoned attempt by a different user,
        the task should not be available.
        """
        user = UserFactory.create()
        other_user = UserFactory.create()
        task = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(user=other_user, state=TaskAttempt.ABANDONED, task=task)
        eq_(task.is_available_to_user(user), True)

    def test_isnt_available_to_user_other_user_non_abandoned_attempt(self):
        """
        If there is a non-abandoned attempt by a different user,
        the task should not be available.
        """
        user = UserFactory.create()
        other_user = UserFactory.create()
        task = TaskFactory.create(repeatable=False)
        TaskAttemptFactory.create(user=other_user, state=TaskAttempt.STARTED, task=task)
        eq_(task.is_available_to_user(user), False)

    def test_is_taken_taken_task(self):
        """
        If there is a started attempt,
        the task should be taken.
        """
        eq_(self.task_not_repeatable_started_attempt.is_taken, True)

    def test_isnt_taken_finished_task(self):
        """
        If there is a finished attempt,
        the task should not be taken.
        """
        eq_(self.task_not_repeatable_finished_attempt.is_taken, False)

    def test_isnt_taken_abandoned_task(self):
        """
        If there is an abandoned attempt,
        the task should not be taken.
        """
        eq_(self.task_not_repeatable_abandoned_attempt.is_taken, False)

    def test_isnt_taken_no_attempts_task(self):
        """
        If there are no attempts,
        the task should not be taken.
        """
        eq_(self.task_not_repeatable_no_attempts.is_taken, False)

    def test_is_completed_finished_task(self):
        """
        If there is a finished attempt,
        the task should be completed.
        """
        eq_(self.task_not_repeatable_finished_attempt.is_completed, True)

    def test_isnt_completed_taken_task(self):
        """
        If there is a started attempt,
        the task should not be completed.
        """
        eq_(self.task_not_repeatable_started_attempt.is_completed, False)

    def test_isnt_completed_abandoned_task(self):
        """
        If there is an abandoned attempt,
        the task should not be completed.
        """
        eq_(self.task_not_repeatable_abandoned_attempt.is_completed, False)

    def test_isnt_completed_no_attempts_task(self):
        """
        If there are no attempts,
        the task should not be completed.
        """
        eq_(self.task_not_repeatable_no_attempts.is_completed, False)
