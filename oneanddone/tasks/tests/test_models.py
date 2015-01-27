# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime, timedelta

from django.test.utils import override_settings
from django.utils import timezone

from mock import patch
from nose.tools import eq_, ok_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.models import (Task, TaskAttempt, TaskInvalidationCriterion,
                                     TaskKeyword)
from oneanddone.tasks.tests import (BugzillaBugFactory, FeedbackFactory,
                                    TaskFactory, TaskImportBatchFactory,
                                    TaskInvalidationCriterionFactory, TaskKeywordFactory,
                                    TaskAttemptFactory, ValidTaskAttemptFactory)
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
        self.task_invalid = TaskFactory.create(is_invalid=True)
        self.task_no_draft = TaskFactory.create(is_draft=False)
        self.task_start_jan = TaskFactory.create(
            is_draft=False, start_date=aware_datetime(2014, 1, 1))
        self.task_end_jan = TaskFactory.create(is_draft=False, end_date=aware_datetime(2014, 1, 1))
        self.task_range_jan_feb = TaskFactory.create(
            is_draft=False, start_date=aware_datetime(2014, 1, 1),
            end_date=aware_datetime(2014, 2, 1))

    def test_bugzilla_bug_exists(self):
        bug = BugzillaBugFactory.create()
        task = TaskFactory.create(imported_item=bug)
        with patch('oneanddone.tasks.models.BugzillaUtils.request_bug') as request_bug:
            request_bug.return_value = bug
            eq_(bug, task.bugzilla_bug)
            request_bug.assert_called_with(bug.bugzilla_id)

    def test_bugzilla_bug_not_exists(self):
        task = TaskFactory.create()
        eq_(None, task.bugzilla_bug)

    def test_default_sort_order(self):
        """
        The sort order of tasks should default to `priority`, `difficulty`
        """
        Task.objects.all().delete()
        t3, t1, t4, t2, t6, t5 = TaskFactory.create_batch(6)
        t1.priority = 1
        t1.difficulty = 1
        t1.save()
        t2.priority = 1
        t2.difficulty = 2
        t2.save()
        t3.priority = 1
        t3.difficulty = 3
        t3.save()
        t4.priority = 2
        t4.difficulty = 1
        t4.save()
        t5.priority = 2
        t5.difficulty = 3
        t5.save()
        t6.priority = 3
        t6.difficulty = 1
        t6.save()
        tasks = Task.objects.all()
        eq_(tasks[0], t1)
        eq_(tasks[1], t2)
        eq_(tasks[2], t3)
        eq_(tasks[3], t4)
        eq_(tasks[4], t5)
        eq_(tasks[5], t6)

    def test_first_previous_task(self):
        task1, task2, task3 = TaskFactory.create_batch(3)
        eq_(task2.first_previous_task, None)
        task1.next_task = task2
        task1.save()
        task3.next_task = task2
        task3.save()
        eq_(task1, task2.first_previous_task)

    def test_get_next_task_url(self):
        task1, task2 = TaskFactory.create_batch(2)
        eq_(task1.get_next_task_url(), '')
        task2.next_task = task1
        task2.save()
        ok_(str(task1.id) in task2.get_next_task_url())

    def test_has_bugzilla_bug_false(self):
        task = TaskFactory.create()
        ok_(not task.has_bugzilla_bug)

    def test_has_bugzilla_bug_true(self):
        bug = BugzillaBugFactory.create()
        task = TaskFactory.create(imported_item=bug)
        ok_(task.has_bugzilla_bug)

    def test_invalidate_tasks_equals_criterion(self):
        """
        The invalidate_tasks routine should invalidate tasks which match the
        invalidation criteria.
        This tests an equals criterion.
        """
        bug_to_become_invalid, bug_to_stay_valid = BugzillaBugFactory.create_batch(2)
        batch = TaskImportBatchFactory.create()
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.EQUAL,
            field_value='value')
        criterion.batches.add(batch)
        criterion.save()
        task1, task2, task3 = TaskFactory.create_batch(3,
                                                       batch=batch,
                                                       imported_item=bug_to_become_invalid,
                                                       is_invalid=False)
        task3.imported_item = bug_to_stay_valid
        task3.save()
        with patch('oneanddone.tasks.models.BugzillaUtils.request_bug') as request_bug:
            request_bug.side_effect = lambda x: {
                bug_to_become_invalid.bugzilla_id: {'name': 'value'},
                bug_to_stay_valid.bugzilla_id: {'name': 'not value'}}[x]
            eq_(Task.invalidate_tasks(), 2)
        eq_(Task.objects.get(pk=task1.pk).is_invalid, True)
        eq_(Task.objects.get(pk=task2.pk).is_invalid, True)
        eq_(Task.objects.get(pk=task3.pk).is_invalid, False)

    def test_invalidate_tasks_not_equals_criterion(self):
        """
        The invalidate_tasks routine should invalidate tasks which match the
        invalidation criteria.
        This tests a not equals criterion.
        """
        bug_to_become_invalid, bug_to_stay_valid = BugzillaBugFactory.create_batch(2)
        batch = TaskImportBatchFactory.create()
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.NOT_EQUAL,
            field_value='value')
        criterion.batches.add(batch)
        criterion.save()
        task1, task2 = TaskFactory.create_batch(2,
                                                batch=batch,
                                                imported_item=bug_to_become_invalid,
                                                is_invalid=False)
        task2.imported_item = bug_to_stay_valid
        task2.save()
        with patch('oneanddone.tasks.models.BugzillaUtils.request_bug') as request_bug:
            request_bug.side_effect = lambda x: {
                bug_to_become_invalid.bugzilla_id: {'name': 'value'},
                bug_to_stay_valid.bugzilla_id: {'name': 'not value'}}[x]
            eq_(Task.invalidate_tasks(), 1)
        eq_(Task.objects.get(pk=task1.pk).is_invalid, False)
        eq_(Task.objects.get(pk=task2.pk).is_invalid, True)

    def test_invalidation_criteria_does_not_exist(self):
        task = TaskFactory.create()
        eq_(None, task.invalidation_criteria)

    def test_invalidation_criteria_exists(self):
        batch = TaskImportBatchFactory.create()
        criterion = TaskInvalidationCriterionFactory.create()
        criterion.batches.add(batch)
        criterion.save()
        task = TaskFactory.create(batch=batch)
        eq_(criterion, task.invalidation_criteria[0])

    def test_isnt_available_invalid(self):
        """
        If a task is marked as invalid, it should not be available.
        """
        eq_(self.task_invalid.is_available, False)

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

    def test_is_available_filter_invalid(self):
        """
        If a task is marked as invalid, it should not be available.
        """
        tasks = Task.objects.filter(Task.is_available_filter(now=aware_datetime(2014, 1, 2)))
        ok_(self.task_no_draft in tasks)
        ok_(self.task_invalid not in tasks)

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

    def test_keywords_list_returns_expected_string(self):
        """
        keywords_list should return a comma delimited list of keywords.
        """
        TaskKeywordFactory.create_batch(4, task=self.task_draft)
        keywords = TaskKeyword.objects.filter(task=self.task_draft)
        expected_keywords = ', '.join([keyword.name for keyword in keywords])
        eq_(self.task_draft.keywords_list, expected_keywords)

    def test_save_closes_task_attempts(self):
        """
        When a saved task is unavailable,
        close any open attempts, and set the attempts
        to require a notification.
        """
        user1 = UserFactory.create()
        user2 = UserFactory.create()
        TaskAttemptFactory.create(
            user=user1,
            state=TaskAttempt.STARTED,
            task=self.task_no_draft)
        TaskAttemptFactory.create(
            user=user2,
            state=TaskAttempt.STARTED,
            task=self.task_no_draft)
        eq_(self.task_no_draft.taskattempt_set.filter(state=TaskAttempt.STARTED).count(), 2)
        self.task_no_draft.is_draft = True
        self.task_no_draft.save()
        eq_(TaskAttempt.objects.filter(task=self.task_no_draft,
                                       state=TaskAttempt.STARTED).count(), 0)
        eq_(TaskAttempt.objects.filter(task=self.task_no_draft,
                                       state=TaskAttempt.CLOSED,
                                       requires_notification=True).count(), 2)


class TaskMetricsSupportTests(TestCase):
    def setUp(self):
        self.user1, self.user2 = UserFactory.create_batch(2)
        self.task1, self.task2 = TaskFactory.create_batch(2)
        TaskAttemptFactory.create_batch(2,
                                        user=self.user1,
                                        task=self.task1,
                                        state=TaskAttempt.FINISHED)
        ValidTaskAttemptFactory.create_batch(2,
                                             user=self.user1,
                                             task=self.task1,
                                             state=TaskAttempt.FINISHED)
        ValidTaskAttemptFactory.create(user=self.user1,
                                       task=self.task2,
                                       state=TaskAttempt.FINISHED)
        ValidTaskAttemptFactory.create(user=self.user2,
                                       task=self.task1,
                                       state=TaskAttempt.FINISHED)
        ValidTaskAttemptFactory.create_batch(2,
                                             user=self.user1,
                                             task=self.task1,
                                             state=TaskAttempt.ABANDONED)
        ValidTaskAttemptFactory.create(user=self.user2,
                                       task=self.task1,
                                       state=TaskAttempt.ABANDONED)
        ValidTaskAttemptFactory.create(user=self.user1,
                                       task=self.task2,
                                       state=TaskAttempt.ABANDONED)
        ValidTaskAttemptFactory.create_batch(2,
                                             user=self.user1,
                                             task=self.task1,
                                             state=TaskAttempt.CLOSED)
        ValidTaskAttemptFactory.create(user=self.user2,
                                       task=self.task1,
                                       state=TaskAttempt.CLOSED)
        ValidTaskAttemptFactory.create(user=self.user1,
                                       task=self.task2,
                                       state=TaskAttempt.CLOSED)

    def test_abandoned_attempts(self):
        eq_(len(self.task1.abandoned_attempts), 3)

    def test_abandoned_user_count(self):
        eq_(self.task1.abandoned_user_count, 2)

    def test_all_attempts(self):
        eq_(len(self.task1.all_attempts), 11)

    def test_closed_attempts(self):
        eq_(len(self.task1.closed_attempts), 3)

    def test_closed_user_count(self):
        eq_(self.task1.closed_user_count, 2)

    @override_settings(MIN_DURATION_FOR_COMPLETED_ATTEMPTS=10)
    def test_completed_attempts(self):
        eq_(len(self.task1.completed_attempts), 3)

    @override_settings(MIN_DURATION_FOR_COMPLETED_ATTEMPTS=10)
    def test_completed_user_count(self):
        eq_(self.task1.completed_user_count, 2)

    def test_incomplete_attempts(self):
        eq_(len(self.task1.incomplete_attempts), 6)

    def test_incomplete_user_count(self):
        eq_(self.task1.incomplete_user_count, 2)

    @override_settings(MIN_DURATION_FOR_COMPLETED_ATTEMPTS=10)
    def test_too_short_completed_attempts(self):
        eq_(len(self.task1.too_short_completed_attempts), 2)

    def test_users_who_completed_this_task(self):
        ql = self.task1.users_who_completed_this_task
        eq_(len(ql), 2)
        eq_(ql[0], self.user1)
        eq_(ql[1], self.user2)


class TaskAttemptTests(TestCase):
    def setUp(self):
        TaskAttempt.objects.all().delete()
        user = UserFactory.create()
        task = TaskFactory.create()
        self.attempt = TaskAttemptFactory.create(user=user, task=task)

    def test_attempt_length_in_minutes(self):
        """
        Return the time, in minutes between the attempt creation time and
        last modification time.
        """
        self.attempt.created = aware_datetime(2014, 1, 1)
        self.attempt.modified = aware_datetime(2014, 1, 2)
        eq_(self.attempt.attempt_length_in_minutes, 1440)

    def test_close_expired_task_attempts(self):
        """
        The close_expired_task_attempts routine should close all
        attempts for tasks that are no longer available,
        set them as requiring notification,
        and return the number that were closed.
        """
        task_no_expire = TaskFactory.create()
        task = TaskFactory.create(end_date=timezone.now() + timedelta(days=1))
        future_date = timezone.now() + timedelta(days=2)
        user1, user2, user3 = UserFactory.create_batch(3)
        TaskAttemptFactory.create(
            user=user1,
            state=TaskAttempt.STARTED,
            task=task)
        TaskAttemptFactory.create(
            user=user2,
            state=TaskAttempt.STARTED,
            task=task)
        TaskAttemptFactory.create(
            user=user3,
            state=TaskAttempt.STARTED,
            task=task_no_expire)
        eq_(task.taskattempt_set.filter(state=TaskAttempt.STARTED).count(), 2)
        eq_(task_no_expire.taskattempt_set.filter(state=TaskAttempt.STARTED).count(), 1)
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = future_date
            eq_(TaskAttempt.close_expired_task_attempts(), 2)
        eq_(TaskAttempt.objects.filter(task=task,
                                       state=TaskAttempt.STARTED).count(), 0)
        eq_(TaskAttempt.objects.filter(task=task,
                                       state=TaskAttempt.CLOSED,
                                       requires_notification=True).count(), 2)
        eq_(TaskAttempt.objects.filter(task=task_no_expire,
                                       state=TaskAttempt.STARTED).count(), 1)

    def test_close_stale_onetime_attempts(self):
        """
        The close_stale_onetime_attempts routine should close all
        expired one-time attempts, set them as requiring notification,
        and return the number that were closed.
        """
        task = TaskFactory.create(repeatable=False)
        user = UserFactory.create()
        recent_attempt, expired_attempt_1, expired_attempt_2 = TaskAttemptFactory.create_batch(
            3,
            user=user,
            state=TaskAttempt.STARTED,
            task=task)
        recent_attempt.created = aware_datetime(2014, 1, 29)
        recent_attempt.save()
        expired_attempt_1.created = aware_datetime(2014, 1, 1)
        expired_attempt_1.save()
        expired_attempt_2.created = aware_datetime(2014, 1, 1)
        expired_attempt_2.save()
        eq_(task.taskattempt_set.filter(state=TaskAttempt.STARTED).count(), 3)
        with patch('oneanddone.tasks.models.timezone.now') as now:
            now.return_value = aware_datetime(2014, 1, 31)
            eq_(TaskAttempt.close_stale_onetime_attempts(), 2)
        eq_(TaskAttempt.objects.filter(task=task,
                                       state=TaskAttempt.STARTED).count(), 1)
        eq_(TaskAttempt.objects.filter(task=task,
                                       state=TaskAttempt.CLOSED,
                                       requires_notification=True).count(), 2)

    def test_feedback_display_none(self):
        """
        If no feedback exists for an attempt, return a standard string.
        """
        eq_(self.attempt.feedback_display, 'No feedback for this attempt')

    def test_feedback_display_text(self):
        """
        If feedback exists for an attempt, return the feedback text.
        """
        feedback_text = 'Feedback text'
        FeedbackFactory.create(attempt=self.attempt, text=feedback_text)
        eq_(self.attempt.feedback_display, feedback_text)

    def test_has_feedback_false(self):
        """
        If no feedback exists return False.
        """
        eq_(self.attempt.has_feedback, False)

    def test_has_feedback_true(self):
        """
        If feedback exists return True.
        """
        FeedbackFactory.create(attempt=self.attempt)
        eq_(self.attempt.has_feedback, True)

    def test_next_task(self):
        attempt = self.attempt
        task2 = TaskFactory.create()
        eq_(attempt.next_task, None)
        attempt.task.next_task = task2
        attempt.task.save()
        eq_(attempt.next_task, task2)


class TaskInvalidationCriterionTests(TestCase):

    def test_equal_passes_false(self):
        """
        Return false if the criterion does not pass for the bug, using EQUAL.
        """
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.EQUAL,
            field_value='value')
        bug = {'name': 'not value'}
        ok_(not criterion.passes(bug))

    def test_equal_passes_true(self):
        """
        Return true if the criterion passes for the bug, using EQUAL.
        """
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.EQUAL,
            field_value='value')
        bug = {'name': 'value'}
        ok_(criterion.passes(bug))

    def test_not_equal_passes_false(self):
        """
        Return false if the criterion does not pass for the bug, using NOT_EQUAL.
        """
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.NOT_EQUAL,
            field_value='value')
        bug = {'name': 'value'}
        ok_(not criterion.passes(bug))

    def test_not_equal_passes_true(self):
        """
        Return true if the criterion passes for the bug, using NOT_EQUAL.
        """
        criterion = TaskInvalidationCriterionFactory.create(
            field_name='name',
            relation=TaskInvalidationCriterion.NOT_EQUAL,
            field_value='not value')
        bug = {'name': 'value'}
        ok_(criterion.passes(bug))
