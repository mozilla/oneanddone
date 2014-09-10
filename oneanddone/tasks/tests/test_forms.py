# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.http import Http404

from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.forms import TaskForm
from oneanddone.tasks.models import TaskKeyword
from oneanddone.tasks.tests import TaskFactory, TaskKeywordFactory
from oneanddone.users.tests import UserFactory


def get_filled_taskform(task, **kwargs):
    """
    Returns a TaskForm populated with initial task fields and additional
    fields provided as keyword arguments.
    Additional fields overwrite any matching initial fields.
    """
    data = {'team': task.team.id}
    for field in ('name', 'short_description', 'execution_time', 'difficulty',
                  'repeatable', 'instructions', 'is_draft', 'priority'):
            data[field] = getattr(task, field)
    data.update(kwargs)
    return TaskForm(instance=task, data=data)


class TaskFormTests(TestCase):

    def test_initial_contains_list_of_keywords_for_existing_task(self):
        """
        Initial should contain the list of keywords from the task instance.
        """
        task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=task)
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], 'test1, test2, test3')

    def test_initial_contains_empty_list_of_keywords_for_new_task(self):
        """
        Initial should contain an empty list of keywords for a new task.
        """
        task = TaskFactory.create()
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], '')

    def test_save_processes_keywords_correctly(self):
        """
        Saving the form should update the keywords correctly.
        - Removed keywords should be removed
        - New keywords should be added
        - Remaining keywords should remain
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=task)
        form = get_filled_taskform(task, keywords='test3, new_keyword')
        form.save(user)

        removed_keyword = TaskKeyword.objects.filter(task=task, name='test1')
        eq_(len(removed_keyword), 0)

        added_keyword = TaskKeyword.objects.filter(task=task, name='new_keyword')
        eq_(len(added_keyword), 1)

        kept_keyword = TaskKeyword.objects.filter(task=task, name='test3')
        eq_(len(kept_keyword), 1)

        # double-check on the keywords_list property
        eq_(task.keywords_list, 'test3, new_keyword')

    def test_save_does_not_add_a_blank_keyword(self):
        """
        Saving the form should not add a blank keyword when
         keywords are empty.
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        form = get_filled_taskform(task, keywords=' ')

        form.save(user)

        eq_(task.keyword_set.count(), 0)

    def test_validation_start_date_before_end_date(self):
        """
        The form is valid if start date is before end date and all other
        field requirements are respected.
        """
        form = get_filled_taskform(TaskFactory.create(),
                                   start_date='2013-07-01',
                                   end_date='2013-08-15')

        self.assertTrue(form.is_valid())

    def test_validation_start_date_after_end_date(self):
        """
        The form is not valid if start date is after end date.
        """
        form = get_filled_taskform(TaskFactory.create(),
                                   start_date='2014-07-01',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(), ["'End date' must be after 'Start date'"])

    def test_validation_same_start_date_as_end_date(self):
        """
        The form is not valid if start date is same as end date.
        """
        form = get_filled_taskform(TaskFactory.create(),
                                   start_date='2013-08-15',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(), ["'End date' must be after 'Start date'"])
