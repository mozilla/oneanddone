# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views import generic

from braces.views import LoginRequiredMixin
from datetime import date, timedelta
from django_filters.views import FilterView
from rest_framework import generics
from tower import ugettext as _, ugettext_lazy as _lazy

from oneanddone.base.util import get_object_or_none, SortHeaders
from oneanddone.tasks.filters import ActivityFilterSet, TasksFilterSet
from oneanddone.tasks.forms import (FeedbackForm, PreviewConfirmationForm,
                                    TaskImportBatchForm,
                                    TaskInvalidCriteriaFormSet, TaskForm)
from oneanddone.tasks.mixins import (APIRecordCreatorMixin,
                                     APIOnlyCreatorMayDeleteMixin)
from oneanddone.tasks.mixins import (TaskMustBeAvailableMixin,
                                     HideNonRepeatableTaskMixin)
from oneanddone.tasks.mixins import GetUserAttemptMixin
from oneanddone.tasks.models import (BugzillaBug, Feedback, Task, TaskAttempt,
                                     TaskMetrics)
from oneanddone.tasks.serializers import TaskSerializer
from oneanddone.users.mixins import (MyStaffUserRequiredMixin,
                                     PrivacyPolicyRequiredMixin)


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
                'elapsed_time': 'TIMESTAMPDIFF(SECOND, tasks_taskattempt.created, tasks_taskattempt.modified)'
            })
        return qs.order_by(self.sort_headers.get_order_by())


class AvailableTasksView(TaskMustBeAvailableMixin, FilterView):
    queryset = Task.objects.all()
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 10
    filterset_class = TasksFilterSet


class CreateFeedbackView(LoginRequiredMixin, PrivacyPolicyRequiredMixin,
                         HideNonRepeatableTaskMixin, GetUserAttemptMixin,
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
        task_name = feedback.attempt.task.name
        subject = 'Feedback on %s from One and Done' % task_name
        task_link = 'http'
        if self.request.is_secure():
            task_link += 's'
        task_link += '://%s%s' % (
            self.request.get_host(),
            feedback.attempt.task.get_absolute_url())
        template = get_template('tasks/emails/feedback_email.txt')

        message = template.render({
            'feedback_user': feedback.attempt.user,
            'task_name': task_name,
            'task_link': task_link,
            'task_state': feedback.attempt.get_state_display(),
            'feedback': feedback.text})

        # Manually replace quotes and double-quotes as these get
        # escaped by the template and this makes the message look bad.
        filtered_message = message.replace('&#34;', '"').replace('&#39;', "'")

        send_mail(
            subject,
            filtered_message,
            'oneanddone@mozilla.com',
            [feedback.attempt.task.creator.email])

        messages.success(self.request, _('Your feedback has been submitted. Thanks!'))
        return redirect('base.home')


class CreateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateTaskView, self).get_context_data(*args, **kwargs)
        ctx['task_form'] = ctx.get('form')
        ctx['action'] = 'Add'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been created.'))
        return redirect('tasks.list')


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
                             'repeatable': False}
        task_form = TaskForm(instance=None, prefix='task', **kwargs)

        forms = {'criterion_formset': criterion_formset,
                 'batch_form': batch_form,
                 'task_form': task_form}

        # Create a hidden form for each possible PreviewConfirmationForm stage.
        # These forms are used to signal what the next stage should be.
        make_stage = lambda x: PreviewConfirmationForm(data={'stage': x})
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


class MetricsView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.ListView):
    list_headers = (
        (_lazy(u'Task'), 'task__name'),
        (_lazy(u'Users Completed'), 'completed_users',
         _lazy(u'Number of unique users who completed the task')),
        (_lazy(u'Users Abandoned'), 'abandoned_users',
         _lazy(u'Number of unique users who explicitly abandoned the task')),
        (_lazy(u'Users Did Not Complete'), 'incomplete_users',
         _lazy(u'Number of unique users who took but never completed the task')),
        (_lazy(u'Moves on to Another'), 'user_completes_then_takes_another_count',
         _lazy(u'Number of times the task was completed and the the same user takes another task')),
        (_lazy(u'Takes No Further Tasks'), 'user_takes_then_quits_count',
         _lazy(u'Number of times the task was taken and then the same user takes no further tasks')),
    )
    context_object_name = 'metrics'
    template_name = 'tasks/metrics.html'
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        ctx = super(MetricsView, self).get_context_data(*args, **kwargs)
        ctx['headers'] = self.sort_headers
        return ctx

    def get_queryset(self):
        self.sort_headers = SortHeaders(self.request, self.list_headers,
                                        default_order_field=1,
                                        default_order_type='desc')
        qs = TaskMetrics.objects.all()
        return qs.order_by(self.sort_headers.get_order_by())


class RandomTasksView(TaskMustBeAvailableMixin, generic.ListView):
    queryset = Task.objects.order_by('?')
    template_name = 'tasks/random.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RandomTasksView, self).get_context_data(*args, **kwargs)
        # Only return 5 tasks
        ctx['random_task_list'] = ctx['object_list'][:5]
        return ctx


class StartTaskView(PrivacyPolicyRequiredMixin, HideNonRepeatableTaskMixin,
                    generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        # Do not allow users to take more than one task at a time
        if self.request.user.attempts_in_progress.exists():
            messages.error(self.request, _('You may only work on one task at a time.'))
            return redirect('base.home')

        task = self.get_object()
        if not task.is_available:
            messages.error(self.request, _('That task is unavailable at this time.'))
            return redirect('tasks.available')

        attempt, created = TaskAttempt.objects.get_or_create(user=self.request.user, task=task,
                                                             state=TaskAttempt.STARTED)
        return redirect(task)


class TaskAttemptView(PrivacyPolicyRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
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


class TaskDetailView(generic.DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    allow_expired_tasks = True

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskDetailView, self).get_context_data(*args, **kwargs)
        task = self.object
        if self.request.user.is_authenticated():
            ctx['attempt'] = get_object_or_none(TaskAttempt, user=self.request.user,
                                                task=task, state=TaskAttempt.STARTED)

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
        return redirect('tasks.list')


class TaskDetailAPI(APIOnlyCreatorMayDeleteMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
