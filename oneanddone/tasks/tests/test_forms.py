# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from nose.tools import assert_not_in, eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.forms import TaskForm
from oneanddone.tasks.models import TaskKeyword
from oneanddone.tasks.tests import TaskFactory, TaskKeywordFactory
from oneanddone.users.tests import UserProfileFactory


def get_filled_taskform(task, **kwargs):
    """
    Returns a TaskForm populated with initial task fields and additional
    fields provided as keyword arguments.
    Additional fields overwrite any matching initial fields.
    """
    data = {'team': task.team.id, 'owner': task.owner.id}
    for field in ('name', 'short_description', 'execution_time', 'difficulty',
                  'repeatable', 'instructions', 'is_draft', 'is_invalid', 'priority'):
            data[field] = getattr(task, field)
    data.update(kwargs)
    return TaskForm(instance=task, data=data)


class TaskFormTests(TestCase):

    def setUp(self):
        self.user = UserProfileFactory.create(user__is_staff=True, name='Foo bar').user
        self.task = TaskFactory.create(owner=self.user)

    def test_form_widgets_have_expected_class(self):
        """
        Classes specified in attrs in form definition should be
        populated into the widgets
        """
        form = TaskForm(instance=None)
        for field in ('name', 'short_description', 'instructions',
                      'why_this_matters', 'prerequisites'):
            eq_(form[field].field.widget.attrs['class'], 'fill-width')

    def test_initial_contains_empty_list_of_keywords_for_new_task(self):
        """
        Initial should contain an empty list of keywords for a new task.
        """
        task = TaskFactory.create()
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], '')

    def test_initial_contains_list_of_keywords_for_existing_task(self):
        """
        Initial should contain the list of keywords from the task instance.
        """
        task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=task)
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], 'test1, test2, test3')

    def test_save_does_not_add_a_blank_keyword(self):
        """
        Saving the form should not add a blank keyword when
         keywords are empty.
        """
        form = get_filled_taskform(self.task, keywords=' ')

        form.save(self.user)

        eq_(self.task.keyword_set.count(), 0)

    def test_save_processes_keywords_correctly(self):
        """
        Saving the form should update the keywords correctly.
        - Removed keywords should be removed
        - New keywords should be added
        - Remaining keywords should remain
        """
        TaskKeywordFactory.create_batch(3, task=self.task)
        form = get_filled_taskform(self.task, keywords='test3, new_keyword')
        form.save(self.user)

        removed_keyword = TaskKeyword.objects.filter(task=self.task, name='test1')
        eq_(len(removed_keyword), 0)

        added_keyword = TaskKeyword.objects.filter(task=self.task, name='new_keyword')
        eq_(len(added_keyword), 1)

        kept_keyword = TaskKeyword.objects.filter(task=self.task, name='test3')
        eq_(len(kept_keyword), 1)

        # double-check on the keywords_list property
        eq_(self.task.keywords_list, 'test3, new_keyword')

    def test_save_processes_keywords_for_clone(self):
        """
        When the keywords field is filled initially but submitted with no
        changes, the form processes these keywords anyway.
        Therefore, when cloning a task, the new task is saved with the same
        keywords as the original task.
        """
        form = get_filled_taskform(self.task)
        keywords = 'test1, test2, test3'
        form.initial['keywords'] = form.data['keywords'] = keywords
        form.save(self.user)
        assert_not_in('keywords', form.changed_data)
        eq_(self.task.keywords_list, keywords)

    def test_validation_same_start_date_as_end_date(self):
        """
        The form is not valid if start date is same as end date.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2013-08-15',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(), ["'End date' must be after 'Start date'"])

    def test_validation_start_date_after_end_date(self):
        """
        The form is not valid if start date is after end date.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2014-07-01',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(), ["'End date' must be after 'Start date'"])

    def test_validation_start_date_before_end_date(self):
        """
        The form is valid if start date is before end date and all other
        field requirements are respected.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2013-07-01',
                                   end_date='2013-08-15')

        self.assertTrue(form.is_valid())
