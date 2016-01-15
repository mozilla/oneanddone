# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _, ugettext_lazy as _lazy
from django.views import generic

from braces.views import LoginRequiredMixin
from datetime import date, timedelta
from django_filters.views import FilterView
from rest_framework import generics

from oneanddone.base.util import get_object_or_none, SortHeaders
from oneanddone.tasks.filters import (ActivityFilterSet, SmallTasksFilterSet,
                                      TasksFilterSet)
from oneanddone.tasks.forms import (FeedbackForm, SubmitVerifiedTaskForm,
                                    PreviewConfirmationForm,
                                    TaskImportBatchForm,
                                    TaskInvalidCriteriaFormSet, TaskForm,
                                    TeamForm)
from oneanddone.tasks.mixins import (APIOnlyCreatorMayDeleteMixin,
                                     APIRecordCreatorMixin,
                                     BaseURLMixin,
                                     GetUserAttemptForFeedbackMixin,
                                     HideNonRepeatableTaskMixin,
                                     TaskMustBeAvailableMixin)
from oneanddone.tasks.models import (BugzillaBug, Feedback, Task, TaskAttempt,
                                     TaskAttemptCommunication, TaskMetrics, TaskTeam)
from oneanddone.tasks.serializers import TaskSerializer
from oneanddone.users.mixins import MyStaffUserRequiredMixin


class ActivityView(LoginRequiredMixin, MyStaffUserRequiredMixin, FilterView):
    list_headers = (
        (_lazy(u'Task'), 'task__name'),
        (_lazy(u'User'), 'user__profile__name'),
        (_lazy(u'Status'), 'state_display'),
        (_lazy(u'Time'), 'elapsed_time'),
    )
    context_object_name = 'attempts'
    template_name = 'tasks/activity.html'
    paginate_by = 20
    filterset_class = ActivityFilterSet

    def get_context_data(self, *args, **kwargs):
        ctx = super(ActivityView, self).get_context_data(*args, **kwargs)
        ctx['headers'] = self.sort_headers
        return ctx

    def get_queryset(self):
        self.sort_headers = SortHeaders(self.request, self.list_headers)
        qs = TaskAttempt.objects.extra(
            select={
                'state_display': TaskAttempt.choice_display_extra_expression('state'),
                'elapsed_time':
                    'EXTRACT(EPOCH FROM (tasks_taskattempt.modified - tasks_taskattempt.created))'
            })
        return qs.order_by(self.sort_headers.get_order_by())


class AvailableTasksView(TaskMustBeAvailableMixin, FilterView):
    queryset = Task.objects.all()
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 10
    filterset_class = TasksFilterSet

    def get_context_data(self, *args, **kwargs):
        ctx = super(AvailableTasksView, self).get_context_data(*args, **kwargs)
        ctx['task_list_heading'] = _('Tasks')
        return ctx


class CreateFeedbackView(LoginRequiredMixin,
                         HideNonRepeatableTaskMixin,
                         GetUserAttemptForFeedbackMixin,
                         BaseURLMixin,
                         generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'tasks/feedback.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateFeedbackView, self).get_context_data(*args, **kwargs)
        ctx['attempt'] = self.attempt
        return ctx

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.attempt = self.attempt
        feedback.save()

        # Send email to task owner
        form.send_email(feedback.attempt, self.base_url, 'feedback', feedback=feedback)

        messages.success(self.request, _('Your feedback has been submitted. Thanks!'))
        return redirect('tasks.whats_next', feedback.attempt.task.id)


class CreateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_form_kwargs(self):
        kwargs = super(CreateTaskView, self).get_form_kwargs()
        kwargs['initial']['owner'] = self.request.user
        if self.kwargs.get('clone'):
            original_task = Task.objects.get(pk=self.kwargs['clone'])
            kwargs['initial'].update(model_to_dict(original_task))
            kwargs['initial']['keywords'] = original_task.keywords_list
            kwargs['initial']['name'] = ' '.join(['Copy of', original_task.name])
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateTaskView, self).get_context_data(*args, **kwargs)
        ctx['task_form'] = ctx.get('form')
        ctx['action'] = 'Add'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def form_valid(self, form):
        task = form.save(self.request.user)

        messages.success(self.request, _('Your task has been created.'))
        return redirect('tasks.detail', task.id)


class ImportTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.TemplateView):

    def get_template_names(self):
        if self.stage == 'preview':
            # After initial form submission
            return ['tasks/confirmation.html']
        else:
            # Initial form load, error or after cancelling from confirmation
            return ['tasks/form.html']

    def get_forms(self):
        kwargs = {'initial': None}
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        batch_form = TaskImportBatchForm(instance=None, prefix='batch',
                                         **kwargs)
        criterion_formset = TaskInvalidCriteriaFormSet(prefix='criterion',
                                                       **kwargs)
        kwargs['initial'] = {'end_date': date.today() + timedelta(days=30),
                             'repeatable': False,
                             'owner': self.request.user}

        task_form = TaskForm(instance=None, prefix='task', **kwargs)

        forms = {'criterion_formset': criterion_formset,
                 'batch_form': batch_form,
                 'task_form': task_form}

        # Create a hidden form for each possible PreviewConfirmationForm stage.
        # These forms are used to signal what the next stage should be.
        def make_stage(stage):
            return PreviewConfirmationForm(data={'stage': stage})
        stages = PreviewConfirmationForm.submission_stages
        forms.update({'stage_form__' + s: make_stage(s) for s in stages})
        return forms

    def get_context_data(self, **kwargs):
        ctx = super(ImportTasksView, self).get_context_data(**kwargs)
        ctx.update(kwargs)
        ctx['action'] = 'Import'
        ctx['import_obj'] = 'tasks'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def forms_valid(self, forms):
        if self.stage == 'confirm':
            return self.done(forms)
        else:
            assert self.stage == 'preview'
            bugs = forms['batch_form'].cleaned_data['_fresh_bugs']
            ctx = forms
            ctx['basename'] = forms['task_form'].cleaned_data['name']
            ctx['bugs'] = bugs
            ctx['num_tasks'] = len(bugs)
            return self.render_to_response(self.get_context_data(**ctx))

    def forms_invalid(self, forms):
        self.stage = 'fill'
        return self.render_to_response(self.get_context_data(**forms))

    def get(self, request, *args, **kwargs):
        # Assume this is a fresh start to the import process
        self.stage = 'fill'
        forms = self.get_forms()
        assert forms['criterion_formset'].total_form_count() == 1
        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        self.stage = self.request.POST.get('stage', 'fill')
        forms = self.get_forms()
        if self.stage == 'fill':
            return self.render_to_response(self.get_context_data(**forms))

        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def done(self, forms):
        bugs = forms['batch_form'].cleaned_data['_fresh_bugs']
        import_batch = forms['batch_form'].save(self.request.user)
        criterion_objs = [criterion_form.cleaned_data['criterion'] for
                          criterion_form in forms['criterion_formset'].forms]
        for criterion in criterion_objs:
            criterion.batches.add(import_batch)
            criterion.save()

        task = forms['task_form'].save(self.request.user, commit=False)
        keywords = [k.strip() for k in forms['task_form'].cleaned_data['keywords'].split(',')]
        task.batch = import_batch
        basename = task.name
        for bug in bugs:
            bug_obj, _created = BugzillaBug.objects.get_or_create(bugzilla_id=bug['id'])
            bug_obj.summary = bug['summary']
            bug_obj.save()
            task.pk = None
            task.name = ' '.join([basename, str(bug_obj)])
            task.imported_item = bug_obj
            task.save()
            task.replace_keywords(keywords, self.request.user)

        messages.success(self.request, _('{num} tasks created.').format(num=str(len(bugs))))
        return redirect('tasks.list')


class ListTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, FilterView):
    queryset = Task.objects.all()
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 20
    filterset_class = TasksFilterSet

    def get_context_data(self, *args, **kwargs):
        ctx = super(ListTasksView, self).get_context_data(*args, **kwargs)
        ctx['task_list_heading'] = _('Tasks')
        return ctx


class ListTooShortTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.ListView):
    context_object_name = 'metrics'
    queryset = TaskMetrics.objects.filter(too_short_completed_attempts_count__gt=0)
    template_name = 'tasks/too_short_tasks.html'


class MetricsView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.ListView):
    context_object_name = 'metrics'
    model = TaskMetrics
    template_name = 'tasks/metrics.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(MetricsView, self).get_context_data(*args, **kwargs)
        ctx['averages'] = TaskMetrics.get_averages()
        ctx['medians'] = TaskMetrics.get_medians()
        return ctx


class RandomTasksView(TaskMustBeAvailableMixin, generic.ListView):
    queryset = Task.objects.order_by('?')
    template_name = 'tasks/random.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RandomTasksView, self).get_context_data(*args, **kwargs)
        # Only return 5 tasks
        ctx['random_task_list'] = ctx['object_list'][:5]
        return ctx


class StartTaskView(LoginRequiredMixin, HideNonRepeatableTaskMixin,
                    generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):

        task = self.get_object()
        if not task.is_available:
            messages.error(self.request, _('That task is unavailable at this time.'))
            return redirect('tasks.available')

        attempt, created = TaskAttempt.objects.get_or_create(user=self.request.user, task=task,
                                                             state=TaskAttempt.STARTED)
        return redirect(task)


class TaskAttemptView(LoginRequiredMixin, generic.detail.SingleObjectMixin,
                      generic.View):
    def get_queryset(self):
        return TaskAttempt.objects.filter(user=self.request.user, state=TaskAttempt.STARTED)


class AbandonTaskView(TaskAttemptView):
    def post(self, *args, **kwargs):
        attempt = self.get_object()
        attempt.state = TaskAttempt.ABANDONED
        attempt.save()

        return redirect('tasks.feedback', attempt.pk)


class FinishTaskView(TaskAttemptView):
    def post(self, *args, **kwargs):
        attempt = self.get_object()
        attempt.state = TaskAttempt.FINISHED
        attempt.save()

        return redirect('tasks.feedback', attempt.pk)


class TaskAttemptDetailView(LoginRequiredMixin,
                            MyStaffUserRequiredMixin,
                            generic.View):

    def get(self, request, *args, **kwargs):
        view = TaskAttemptDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SubmitAdminVerificationResponseView.as_view()
        return view(request, *args, **kwargs)


class TaskAttemptDisplayView(LoginRequiredMixin,
                             MyStaffUserRequiredMixin,
                             generic.DetailView):
    model = TaskAttempt
    template_name = 'tasks/attempt_detail.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskAttemptDisplayView, self).get_context_data(*args, **kwargs)
        ctx['form'] = SubmitVerifiedTaskForm()
        return ctx


class SubmitAdminVerificationResponseView(LoginRequiredMixin,
                                          MyStaffUserRequiredMixin,
                                          BaseURLMixin,
                                          generic.detail.SingleObjectMixin,
                                          generic.FormView):

    form_class = SubmitVerifiedTaskForm
    model = TaskAttempt
    template_name = 'tasks/attempt_detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SubmitAdminVerificationResponseView, self).post(request, *args, **kwargs)

    def form_valid(self, form):

        attempt = self.get_object()

        communication = form.save(commit=False)
        communication.attempt = attempt
        communication.type = TaskAttemptCommunication.ADMIN
        communication.creator = self.request.user
        communication.save()

        # Send email to attempt user
        if attempt.user.profile.consent_to_email:
            form.send_email(attempt,
                            self.base_url,
                            'verify_from_admin',
                            communication.content)

        messages.success(self.request, _('Your response to the user has been recorded. Thanks!'))
        return redirect('tasks.attempt', attempt.id)


class TaskVerificationListView(LoginRequiredMixin, MyStaffUserRequiredMixin,
                               generic.ListView):
    queryset = TaskAttempt.objects.filter(state=TaskAttempt.STARTED,
                                          task__must_be_verified=True)
    context_object_name = 'attempts'
    template_name = 'tasks/verification_list.html'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        qs = super(TaskVerificationListView, self).get_queryset(*args, **kwargs)
        return qs.filter(task__owner=self.request.user)


class TaskDetailView(generic.View):

    def get(self, request, *args, **kwargs):
        view = TaskDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SubmitTaskForVerificationView.as_view()
        return view(request, *args, **kwargs)


class TaskDetailContextMixin(object):

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskDetailContextMixin, self).get_context_data(*args, **kwargs)
        task = self.object
        if self.request.user.is_authenticated():
            ctx['attempt'] = get_object_or_none(TaskAttempt, user=self.request.user,
                                                task=task, state=TaskAttempt.STARTED)
        ctx['users'] = task.users_who_completed_this_task

        # add verification form to the context
        if task.must_be_verified:
            if self.request.method == 'GET':
                ctx['verification_form'] = SubmitVerifiedTaskForm()
            elif self.request.method == 'POST':
                ctx['verification_form'] = ctx['form']

        # determine label for Get Started button
        if task.is_taken:
            gs_button_label = _('Taken')
            gs_button_disabled = True
        elif task.is_completed:
            gs_button_label = _('Completed')
            gs_button_disabled = True
        else:
            gs_button_label = _('Get Started')
            gs_button_disabled = False
        ctx['gs_button_label'] = gs_button_label
        ctx['gs_button_disabled'] = gs_button_disabled

        return ctx


class TaskDisplayView(TaskDetailContextMixin, generic.DetailView):
    allow_expired_tasks = True
    model = Task
    template_name = 'tasks/detail.html'


class SubmitTaskForVerificationView(LoginRequiredMixin,
                                    BaseURLMixin,
                                    TaskDetailContextMixin,
                                    generic.detail.SingleObjectMixin,
                                    generic.FormView):

    form_class = SubmitVerifiedTaskForm
    model = Task
    template_name = 'tasks/detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(SubmitTaskForVerificationView, self).post(request, *args, **kwargs)

    def form_valid(self, form):

        attempt = get_object_or_404(TaskAttempt, task=self.get_object(),
                                    user=self.request.user,
                                    state=TaskAttempt.STARTED)

        communication = form.save(commit=False)
        communication.attempt = attempt
        communication.type = TaskAttemptCommunication.USER
        communication.creator = self.request.user
        communication.save()

        # Send email to task owner
        form.send_email(attempt,
                        self.base_url,
                        'verify_from_user',
                        communication.content)

        messages.success(self.request, _('Your request to verify has been submitted. Thanks!'))
        return redirect('tasks.detail', attempt.task.id)


class TeamView(TaskMustBeAvailableMixin, FilterView):
    context_object_name = 'tasks'
    filterset_class = SmallTasksFilterSet
    paginate_by = 10
    queryset = Task.objects.all()
    template_name = 'tasks/team.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(TeamView, self).get_context_data(*args, **kwargs)
        ctx['team'] = TaskTeam.get_team_by_id_or_url_code(self.kwargs)
        ctx['task_list_heading'] = _('%s Tasks' % ctx['team'].name)
        return ctx

    def get_queryset(self, *args, **kwargs):
        qs = super(TeamView, self).get_queryset(*args, **kwargs)
        return qs.filter(team=TaskTeam.get_team_by_id_or_url_code(self.kwargs))


class UpdateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateTaskView, self).get_context_data(*args, **kwargs)
        ctx['task_form'] = ctx.get('form')
        ctx['action'] = 'Update'
        ctx['cancel_url'] = reverse('tasks.detail', args=[self.get_object().id])
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been updated.'))
        return redirect('tasks.detail', self.get_object().id)


class UpdateTeamView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.UpdateView):
    model = TaskTeam
    form_class = TeamForm
    template_name = 'tasks/team_form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateTeamView, self).get_context_data(*args, **kwargs)
        ctx['action'] = 'Update'
        ctx['cancel_url'] = reverse('tasks.team', args=[self.get_object().id])
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('The team has been updated.'))
        return redirect('tasks.team', self.get_object().id)


class VerifyTaskView(LoginRequiredMixin,
                     MyStaffUserRequiredMixin,
                     BaseURLMixin,
                     generic.detail.SingleObjectMixin,
                     generic.View):

    model = TaskAttempt

    def post(self, *args, **kwargs):
        attempt = self.get_object()
        attempt.state = TaskAttempt.FINISHED
        attempt.save()

        # Send email to attempt user
        if attempt.user.profile.consent_to_email:
            SubmitVerifiedTaskForm().send_email(attempt,
                                                self.base_url,
                                                'verified')

        return redirect('tasks.attempt', attempt.pk)


class WhatsNextView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'tasks/whats_next.html'


class TaskDetailAPI(APIOnlyCreatorMayDeleteMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
