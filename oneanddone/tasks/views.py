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
from django_filters.views import FilterView
from rest_framework import generics
from tower import ugettext as _

from oneanddone.base.util import get_object_or_none
from oneanddone.tasks.filters import TasksFilterSet
from oneanddone.tasks.forms import FeedbackForm, TaskForm
from oneanddone.tasks.mixins import APIRecordCreatorMixin, APIOnlyCreatorMayDeleteMixin
from oneanddone.tasks.mixins import TaskMustBeAvailableMixin, HideNonRepeatableTaskMixin
from oneanddone.tasks.mixins import GetUserAttemptMixin
from oneanddone.tasks.models import Feedback, Task, TaskAttempt
from oneanddone.tasks.serializers import TaskSerializer
from oneanddone.users.mixins import MyStaffUserRequiredMixin, PrivacyPolicyRequiredMixin


class AvailableTasksView(TaskMustBeAvailableMixin, FilterView):
    queryset = Task.objects.all()
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 10
    filterset_class = TasksFilterSet


class RandomTasksView(TaskMustBeAvailableMixin, generic.ListView):
    queryset = Task.objects.order_by('?')
    template_name = 'tasks/random.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RandomTasksView, self).get_context_data(*args, **kwargs)
        # Only return 5 tasks
        ctx['random_task_list'] = ctx['object_list'][:5]
        return ctx


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


class ListTasksView(LoginRequiredMixin, MyStaffUserRequiredMixin, FilterView):
    queryset = Task.objects.all()
    context_object_name = 'tasks'
    template_name = 'tasks/list.html'
    paginate_by = 20
    filterset_class = TasksFilterSet


class CreateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateTaskView, self).get_context_data(*args, **kwargs)
        ctx['action'] = 'Add'
        ctx['cancel_url'] = reverse('tasks.list')
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been created.'))
        return redirect('tasks.list')


class UpdateTaskView(LoginRequiredMixin, MyStaffUserRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(UpdateTaskView, self).get_context_data(*args, **kwargs)
        ctx['action'] = 'Update'
        ctx['cancel_url'] = reverse('tasks.detail', args=[self.get_object().id])
        return ctx

    def form_valid(self, form):
        form.save(self.request.user)

        messages.success(self.request, _('Your task has been updated.'))
        return redirect('tasks.list')


class TaskListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailAPI(APIOnlyCreatorMayDeleteMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
