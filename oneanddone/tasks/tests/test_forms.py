# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from mock import patch
from nose.tools import assert_not_in, eq_
from requests.exceptions import RequestException

from oneanddone.base.tests import TestCase
from oneanddone.tasks.forms import (PreviewConfirmationForm,
                                    TaskForm,
                                    TaskImportBatchForm,
                                    TaskInvalidCriteriaFormSet)
from oneanddone.tasks.models import TaskKeyword
from oneanddone.tasks.tests import (BugzillaBugFactory, TaskFactory,
                                    TaskImportBatchFactory, TaskKeywordFactory)
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
        eq_(form.initial['keywords'], 'test2, test1, test0')

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
        eq_(sorted(self.task.keywords_list), sorted('test3, new_keyword'))

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
        eq_(sorted(self.task.keywords_list), sorted(keywords))

    def test_validation_same_start_date_as_end_date(self):
        """
        The form is not valid if start date is same as end date.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2013-08-15',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.errors['start_date'], ["'End date' must be after 'Start date'"])

    def test_validation_start_date_after_end_date(self):
        """
        The form is not valid if start date is after end date.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2014-07-01',
                                   end_date='2013-08-15')

        self.assertFalse(form.is_valid())
        eq_(form.errors['start_date'], ["'End date' must be after 'Start date'"])

    def test_validation_start_date_before_end_date(self):
        """
        The form is valid if start date is before end date and all other
        field requirements are respected.
        """
        form = get_filled_taskform(self.task,
                                   start_date='2013-07-01',
                                   end_date='2013-08-15')

        self.assertTrue(form.is_valid())

    def test_validation_verification_instructions(self):
        """
        The form is not valid if must_be_verified is True but
        verification_instructions is blank.
        """
        form = get_filled_taskform(self.task,
                                   must_be_verified=True)

        self.assertFalse(form.is_valid())
        eq_(form.errors['verification_instructions'],
            ['If the task is a Verified task then you must '
             'provide some verification instructions'])


class PreviewConfirmationFormTests(TestCase):
    def test_validation_invalid_stage(self):
        """
        The form is invalid if the stage is not 'preview', 'confirm' or 'fill'.
        """
        form = PreviewConfirmationForm(data={'stage': 'hug_kitten'})
        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(),
            ['Form data is missing or has been tampered.'])

    def test_validation_missing_stage(self):
        """
        The form is invalid if the stage is not set.
        """
        form = PreviewConfirmationForm(data={'nonsense': ''})
        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(),
            ['Form data is missing or has been tampered.'])


class TaskInvalidCriteriaFormSetTests(TestCase):
    def test_validation_empty_forms(self):
        """
        The formset is invalid if any of its forms are empty.
        """
        # leave the one form in the formset unfilled
        data = {'form-TOTAL_FORMS': u'1',
                'form-INITIAL_FORMS': u'0',
                'form-MAX_NUM_FORMS': u'1000'}
        formset = TaskInvalidCriteriaFormSet(initial=None, data=data)
        self.assertFalse(formset.is_valid())
        eq_(formset.errors, [{'criterion': [u'This field is required.']}])


class TaskImportBatchFormTests(TestCase):
    def test_validation_invalid_query(self):
        """
        The form is invalid when the query has no URL parameters.
        """
        data = {'query': 'http://www.example.com',
                'description': 'foo'}
        form = TaskImportBatchForm(data=data)
        self.assertFalse(form.is_valid())
        eq_(form.non_field_errors(),
            [('For the query URL, please provide '
              'a full URL that includes search '
              'parameters.')])

    def test_validation_no_query_results(self):
        """
        The form is invalid when given a query that returns 0 results.
        """
        data = {'query': 'http://www.example.com?x=y',
                'description': 'foo'}
        with patch('oneanddone.tasks.forms.BugzillaUtils') as BugzillaUtils:
            BugzillaUtils().request_bugcount.return_value = 0
            form = TaskImportBatchForm(data=data)
            self.assertFalse(form.is_valid())
            eq_(form.non_field_errors(), [('Your query does not return'
                                           ' any results.')])

    def test_validation_too_many_query_results(self):
        """
        The form is invalid when given a query that returns more than
        max_results.
        """
        data = {'query': 'http://www.example.com?x=y',
                'description': 'foo'}
        with patch('oneanddone.tasks.forms.BugzillaUtils') as BugzillaUtils:
            BugzillaUtils().request_bugcount.return_value = 101
            form = TaskImportBatchForm(data=data)
            self.assertFalse(form.is_valid())
            eq_(form.non_field_errors(), [('Your query returns more '
                                           'than 100 items.')])

    def test_validation_query_returns_external_error(self):
        """ The form is invalid if given a query that returns any errors """
        data = {'query': 'http://www.example.com?x=y',
                'description': 'foo'}
        with patch('oneanddone.tasks.forms.BugzillaUtils') as BugzillaUtils:
            message = 'bar'
            BugzillaUtils().request_bugcount.side_effect = ValueError(message)
            form = TaskImportBatchForm(data=data)
            self.assertFalse(form.is_valid())
            eq_(form.non_field_errors(), ['External error: ' + message])

    def test_validation_query_returns_bugzilla_error(self):
        """ The form is invalid if given a query that returns any errors """
        data = {'query': 'http://www.example.com?x=y',
                'description': 'foo'}
        with patch('oneanddone.tasks.forms.BugzillaUtils') as BugzillaUtils:
            request_bugcount = BugzillaUtils().request_bugcount
            message = ('Sorry. we cannot retrieve any data from Bugzilla at '
                       'this time. Please report this to the '
                       'One and Done team.')

            request_bugcount.side_effect = RuntimeError
            form = TaskImportBatchForm(data=data)
            self.assertFalse(form.is_valid())
            eq_(form.non_field_errors(), [message])

            request_bugcount.side_effect = RequestException
            form = TaskImportBatchForm(data=data)
            self.assertFalse(form.is_valid())
            eq_(form.non_field_errors(), [message])

    def test_num_fresh_bugs_with_small_new_query(self):
        """
        Given a query that returns n < max_batch_size results, the
        number of fresh bugs in the form's cleaned data is equal to
        n if this is the first time the query is ever submitted.
        """
        max_batch_size = 20
        query_params = 'foo'
        with patch('oneanddone.tasks.forms.BugzillaUtils.request_bugs') as request_bugs:
            # two fresh bugs
            request_bugs.return_value = [{u'id': 50, u'summary': u'foo'},
                                         {u'id': 51, u'summary': u'bar'}]
            query = 'baz'
            n = len(request_bugs())
            fresh_bugs = TaskImportBatchForm._get_fresh_bugs(query,
                                                             query_params,
                                                             n, max_batch_size)
            eq_(len(fresh_bugs), n)

    def test_num_fresh_bugs_with_small_stale_query(self):
        """
        Given a query that returns n < max_batch_size results, the
        number of fresh bugs in the form's cleaned data is equal to 0,
        if the query has been submitted before
        """
        max_batch_size = 20
        query_params = 'foo'
        bug1, bug2 = BugzillaBugFactory.create_batch(2)
        batch1 = TaskImportBatchFactory.create()
        TaskFactory.create_batch(1, batch=batch1, imported_item=bug1,
                                 is_invalid=False)
        TaskFactory.create_batch(1, batch=batch1, imported_item=bug2,
                                 is_invalid=False)
        with patch('oneanddone.tasks.forms.BugzillaUtils.request_bugs') as request_bugs:
            # two bugs previously imported in batch1
            request_bugs.return_value = [{u'id': bug1.bugzilla_id,
                                          u'summary': bug1.summary},
                                         {u'id': bug2.bugzilla_id,
                                          u'summary': bug2.summary}]
            bugs = TaskImportBatchForm._get_fresh_bugs(batch1.query,
                                                       query_params,
                                                       len(request_bugs()),
                                                       max_batch_size)

            eq_(len(bugs), 0)

    def test_num_fresh_bugs_with_big_fresh_query(self):
        """
        Given a query that returns max_batch_size + n results, where
        n < max_batch_size, the first max_batch_size bugs are accepted.
        """
        max_batch_size = 2
        query_params = fresh_query = 'foo'
        with patch('oneanddone.tasks.forms.BugzillaUtils.request_bugs') as request_bugs:
            request_bugs.return_value = [{u'id': 50, u'summary': u'a'},
                                         {u'id': 51, u'summary': u'b'},
                                         {u'id': 52, u'summary': u'c'},
                                         {u'id': 53, u'summary': u'd'}]
            bugs = TaskImportBatchForm._get_fresh_bugs(fresh_query,
                                                       query_params,
                                                       len(request_bugs()),
                                                       max_batch_size)

            eq_(bugs, request_bugs()[:max_batch_size])

    def test_num_fresh_bugs_with_big_stale_query(self):
        """
        Given a query that returns max_batch_size + n results, where
        n < max_batch_size, the number of fresh bugs in the form's
        cleaned data is equal to n the second time the query is submitted
        (Next n bugs are accepted.)
        """
        max_batch_size = 3
        n = 2
        query_params = 'foo'
        db_bugs = BugzillaBugFactory.create_batch(max_batch_size)
        batch1 = TaskImportBatchFactory.create()
        for bug in db_bugs:
            TaskFactory.create_batch(1, batch=batch1, imported_item=bug,
                                     is_invalid=False)

        with patch('oneanddone.tasks.forms.BugzillaUtils.request_bugs') as request_bugs:
            stale_bugs = [{u'id': bug.bugzilla_id, u'summary': bug.summary}
                          for bug in db_bugs]
            new_bugs = [{u'id': 50 + i, u'summary': u'a'} for i in range(n)]
            all_bugs = stale_bugs + new_bugs

            def fake_request(request_params, fields=['id', 'summary'],
                             offset=0, limit=99):
                return all_bugs[offset:offset + limit]

            request_bugs.side_effect = fake_request
            bugs = TaskImportBatchForm._get_fresh_bugs(batch1.query,
                                                       query_params,
                                                       len(all_bugs),
                                                       max_batch_size)
            eq_(bugs, all_bugs[max_batch_size:])
