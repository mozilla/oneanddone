# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.utils.translation import ugettext as _

from mock import Mock, patch
from nose.tools import eq_, ok_, assert_dict_contains_subset

from oneanddone.base.tests import TestCase
from oneanddone.tasks import views
from oneanddone.tasks.forms import (TaskImportBatchForm,
                                    TaskForm,
                                    TaskInvalidCriteriaFormSet)
from oneanddone.tasks.models import (BugzillaBug, Task, TaskAttempt,
                                     TaskImportBatch)
from oneanddone.tasks.tests import (TaskFactory,
                                    TaskImportBatchFactory,
                                    TaskInvalidationCriterionFactory,
                                    TaskKeywordFactory)
from oneanddone.tasks.tests.test_forms import get_filled_taskform
from oneanddone.users.tests import UserFactory


class CreateTaskViewTests(TestCase):
    def setUp(self):
        self.view = views.CreateTaskView()

    def test_get_context_data_returns_add_action_and_url(self):
        """
        The 'Add' action and correct cancel_url
        should be included in the context data.
        """
        context_patch = patch('oneanddone.tasks.views.generic.CreateView.get_context_data')
        with context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['action'], 'Add')
            eq_(ctx['cancel_url'], reverse('tasks.list'))

    def test_get_form_kwargs_sets_initial_owner_to_current_user(self):
        """
        The initial owner for the form should be set to the current user.
        """
        user = UserFactory.create()
        self.view.request = Mock(user=user)
        self.view.kwargs = {}
        with patch('oneanddone.tasks.views.generic.CreateView.get_form_kwargs') as get_form_kwargs:
            get_form_kwargs.return_value = {'initial': {}}
            kwargs = self.view.get_form_kwargs()
        eq_(kwargs['initial']['owner'], user)

    def test_get_form_kwargs_populates_form_with_data_to_be_cloned(self):
        """
        When accessed via the tasks.clone url, the view displays a form
        whose initial data is that of the task being cloned, except for
        the 'name' field, which should be prefixed with 'Copy of '
        """
        user = UserFactory.create()
        original_task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=original_task)
        original_data = get_filled_taskform(original_task).data
        self.view.kwargs = {'clone': original_task.pk}
        self.view.request = Mock(user=user)
        with patch('oneanddone.tasks.views.generic.CreateView.get_form_kwargs') as get_form_kwargs:
            get_form_kwargs.return_value = {'initial': {}}
            initial = self.view.get_form_kwargs()['initial']
        eq_(initial['keywords'], original_task.keywords_list)
        eq_(initial['name'], ' '.join(['Copy of', original_task.name]))
        del original_data['name']
        assert_dict_contains_subset(original_data, initial)


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


class StartTaskViewTests(TestCase):
    def setUp(self):
        self.view = views.StartTaskView()
        self.task = TaskFactory.create()
        self.view.get_object = Mock(return_value=self.task)

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

    def test_post_unavailable_task(self):
        """
        If the task is unavailable, redirect to the available tasks view
        without creating an attempt.
        """
        self.task.is_draft = True
        self.task.save()
        user = UserFactory.create()
        self.view.request = Mock(spec=HttpRequest,
                                 _messages=Mock(),
                                 user=user)

        with patch('oneanddone.tasks.views.redirect') as redirect:
            eq_(self.view.post(), redirect.return_value)
            redirect.assert_called_with('tasks.available')
            ok_(not TaskAttempt.objects.filter(user=user, task=self.task).exists())


class TaskDisplayViewTests(TestCase):
    def setUp(self):
        self.view = views.TaskDisplayView()
        self.view.request = Mock(method='GET')
        self.view.object = Mock()
        self.view.object.name = 'name'

    def test_get_context_data_authenticated(self):
        """
        If the current user is authenticated, fetch their attempt for
        the current task using get_object_or_none.
        """
        self.view.request.user.is_authenticated.return_value = True

        get_object_patch = patch('oneanddone.tasks.views.get_object_or_none')
        context_patch = patch('oneanddone.tasks.views.generic.DetailView.get_context_data')
        with get_object_patch as get_object_or_none, context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()

            eq_(ctx['attempt'], get_object_or_none.return_value)
            get_object_or_none.assert_called_with(TaskAttempt, user=self.view.request.user,
                                                  task=self.view.object, state=TaskAttempt.STARTED)

    def test_get_context_data_available_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request.user.is_authenticated.return_value = False
        self.view.object.is_taken = False
        self.view.object.is_completed = False

        context_patch = patch('oneanddone.tasks.views.generic.CreateView.get_context_data')
        with context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Get Started'))
            eq_(ctx['gs_button_disabled'], False)

    def test_get_context_data_completed_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request.user.is_authenticated.return_value = False
        self.view.object.is_taken = False
        self.view.object.is_completed = True

        context_patch = patch('oneanddone.tasks.views.generic.CreateView.get_context_data')
        with context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Completed'))
            eq_(ctx['gs_button_disabled'], True)

    def test_get_context_data_not_authenticated(self):
        """
        If the current user isn't authenticated, don't include an
        attempt in the context.
        """
        self.view.request.user.is_authenticated.return_value = False

        context_patch = patch('oneanddone.tasks.views.generic.CreateView.get_context_data')
        with context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            ok_('attempt' not in ctx)

    def test_get_context_data_taken_task(self):
        """
        If the task is taken, correct values should be added to the context.
        """
        self.view.request.user.is_authenticated.return_value = False
        self.view.object.is_taken = True

        context_patch = patch('oneanddone.tasks.views.generic.CreateView.get_context_data')
        with context_patch as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['gs_button_label'], _('Taken'))
            eq_(ctx['gs_button_disabled'], True)


class TeamViewTests(TestCase):
    def setUp(self):
        self.view = views.TeamView()
        self.view.request = Mock()
        self.view.object = Mock()
        self.view.object.name = 'name'
        self.view.kwargs = {}

    def test_get_context_data_additional_fields(self):
        """
        context_data should include team and task_list_heading.
        """
        team = Mock()
        team.name = 'team name'

        get_team_patch = patch('oneanddone.tasks.models.TaskTeam.get_team_by_id_or_url_code')
        context_patch = patch('oneanddone.tasks.views.FilterView.get_context_data')
        with get_team_patch as get_team, context_patch as get_context_data:
            get_team.return_value = team
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['team'].name, 'team name')
            eq_(ctx['task_list_heading'], _('team name Tasks'))


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


class ImportTasksViewTests(TestCase):
    def setUp(self):
        self.view = views.ImportTasksView()
        self.view.request = Mock(spec=HttpRequest,
                                 _messages=Mock(),
                                 user=Mock())

    def test_get_context_data_returns_import_action_and_url(self):
        """
        The 'Import' action and correct cancel_url
        should be included in the context data.
        """
        with patch('oneanddone.tasks.views.generic.'
                   'TemplateView.get_context_data') as get_context_data:
            get_context_data.return_value = {}
            ctx = self.view.get_context_data()
            eq_(ctx['action'], 'Import')
            eq_(ctx['cancel_url'], reverse('tasks.list'))

    def test_context_data_after_get_request_has_all_forms(self):
        """ Four forms (task, batch, criterion, stage) should be
            included in the content data.
        """
        self.view.request.method = 'GET'
        response = self.view.get(self.view.request)
        ok_('stage_form__preview' in response.context_data)
        ok_('task_form' in response.context_data)
        ok_('batch_form' in response.context_data)
        ok_('criterion_formset' in response.context_data)

    def test_fill_stage_after_get_request(self):
        """ A GET request to ImportTasksView always yields the
            'fill' stage (i.e. user is entering form data)
        """
        self.view.request.method = 'GET'
        self.view.get(self.view.request)
        eq_(self.view.stage, 'fill')

    def test_form_template_after_get_request(self):
        """ A GET request to the ImportTasksView always yields the
            form.html template stage (i.e. user is entering form data)
        """
        self.view.request.method = 'GET'
        response = self.view.get(self.view.request)
        eq_(response.template_name, ['tasks/form.html'])

    def test_fill_stage_after_preview_form_invalid(self):
        """ Submitting an invalid form to 'preview' is always followed by being
            in the "fill" stage (i.e. user must correct form data)
        """
        bad_forms = {'form': Mock()}
        bad_forms['form'].is_valid.return_value = False
        with patch('oneanddone.tasks.views.ImportTasksView.get_forms') as get_forms:
            get_forms.return_value = bad_forms
            self.view.request.method = 'POST'
            self.view.request.POST = {'stage': 'preview'}
            self.view.post(self.view.request)
            eq_(self.view.stage, 'fill')

    def test_confirmation_template_after_post_and_preview(self):
        """ A POST request to ImportTasksView with stage=preview
            and all forms valid leads to the confirmation.html
            template.
        """
        forms = {'batch_form': Mock(spec=TaskImportBatchForm),
                 'task_form': Mock(spec=TaskForm)}
        forms['batch_form'].is_valid.return_value = True
        forms['batch_form'].cleaned_data = {'_fresh_bugs': ''}
        forms['task_form'].is_valid.return_value = True
        forms['task_form'].cleaned_data = {'name': ''}

        with patch('oneanddone.tasks.views.ImportTasksView.get_forms') as get_forms:
            get_forms.return_value = forms
            self.view.request.method = 'POST'
            self.view.request.POST = {'stage': 'preview'}
            response = self.view.post(self.view.request)
            eq_(response.template_name, ['tasks/confirmation.html'])

    def test_form_template_after_post_and_fill(self):
        """ A POST request to ImportTasksView with stage=fill
            and all forms valid leads to the form.html
            template. (i.e. user is making changes after preview)
        """
        good_forms = {'form': Mock()}
        good_forms['form'].is_valid.return_value = True
        with patch('oneanddone.tasks.views.ImportTasksView.get_forms') as get_forms:
            get_forms.return_value = good_forms
            self.view.request.method = 'POST'
            self.view.request.POST = {'stage': 'fill'}
            response = self.view.post(self.view.request)
            eq_(response.template_name, ['tasks/form.html'])

    def test_form_template_after_post_and_confirm(self):
        """ A POST request to ImportTasksView with stage=confirm
            and all forms valid leads to the tasks.list
        """
        forms = {'batch_form': Mock(spec=TaskImportBatchForm),
                 'task_form': Mock(spec=TaskForm),
                 'criterion_formset': Mock(spec=TaskInvalidCriteriaFormSet)}
        forms['batch_form'].is_valid.return_value = True
        forms['batch_form'].cleaned_data = {'_fresh_bugs': ''}
        forms['task_form'].is_valid.return_value = True
        forms['task_form'].cleaned_data = {'name': '', 'keywords': ''}
        forms['criterion_formset'].is_valid.return_value = True
        forms['criterion_formset'].forms = []

        with patch('oneanddone.tasks.views.ImportTasksView.get_forms') as get_forms:
            with patch('oneanddone.tasks.views.redirect') as redirect:
                get_forms.return_value = forms
                self.view.request.method = 'POST'
                self.view.request.POST = {'stage': 'confirm'}
                eq_(self.view.post(self.view.request), redirect.return_value)
                redirect.assert_called_with('tasks.list')

    def test_create_batch_of_tasks(self):
        def save_batch(user):
            return TaskImportBatchFactory.create(creator=user)

        def save_task(user, **kwargs):
            return TaskFactory.create(creator=user)

        user = UserFactory.create()
        self.view.request = Mock(spec=HttpRequest,
                                 _messages=Mock(),
                                 user=user)
        bugs = [{u'id': 51, u'summary': u'a'}, {u'id': 52, u'summary': u'b'}]
        forms = {'batch_form': Mock(spec=TaskImportBatchForm),
                 'task_form': Mock(spec=TaskForm),
                 'criterion_formset': Mock(spec=TaskInvalidCriteriaFormSet)}
        forms['batch_form'].cleaned_data = {'_fresh_bugs': bugs}
        forms['batch_form'].save.side_effect = save_batch
        forms['task_form'].save.side_effect = save_task
        forms['task_form'].cleaned_data = {'keywords': 'foo, bar'}
        forms['criterion_formset'].forms = [
            Mock(
                cleaned_data={'criterion': TaskInvalidationCriterionFactory.create()})
            for i in range(2)]

        self.view.done(forms)

        batch = TaskImportBatch.objects.get(creator=user)
        BugzillaBug.objects.get(bugzilla_id=51)

        ok_(Task.objects.filter(creator=user,
                                batch=batch).exists())
        eq_(Task.objects.filter(batch=batch).count(), len(bugs))
        eq_(BugzillaBug.objects.count(), len(bugs))
        eq_(batch.taskinvalidationcriterion_set.count(),
            len(forms['criterion_formset'].forms))
        eq_(sorted(Task.objects.filter(batch=batch)[0].keywords_list),
            sorted(forms['task_form'].cleaned_data['keywords']))
