# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic

from django_filters.views import FilterView
from tower import ugettext as _

from oneanddone.base.util import get_object_or_none
from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.tasks.filters import AvailableTasksFilterSet
from oneanddone.tasks.forms import FeedbackForm
from oneanddone.tasks.models import Feedback, Task, TaskAttempt


class AvailableTasksView(UserProfileRequiredMixin, FilterView):
    context_object_name = 'available_tasks'
    template_name = 'tasks/available.html'
    paginate_by = 10
    filterset_class = AvailableTasksFilterSet

    def get_queryset(self):
        now = timezone.now()

        # Only filter by dates if they are not null.
        start_filter = Q(start_date__isnull=True) | Q(start_date__lt=now)
        end_filter = Q(end_date__isnull=True) | Q(end_date__gt=now)

        return (Task.objects
                .filter(start_filter, end_filter)
                .order_by('-execution_time'))


class TaskDetailView(UserProfileRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'tasks/detail.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskDetailView, self).get_context_data(*args, **kwargs)
        ctx['attempt'] = get_object_or_none(TaskAttempt, user=self.request.user, task=self.object,
                                            state=TaskAttempt.STARTED)
        return ctx


class StartTaskView(UserProfileRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        task = self.get_object()
        if not task.is_available:
            messages.error(self.request, _('That task is unavailable at this time.'))
            return redirect('tasks.available')

        attempt, created = TaskAttempt.objects.get_or_create(user=self.request.user, task=task,
                                                             state=TaskAttempt.STARTED)
        return redirect(task)


class AbandonTaskView(UserProfileRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        task = self.get_object()
        attempt = get_object_or_404(TaskAttempt, user=self.request.user, task=task,
                                    state=TaskAttempt.STARTED)
        attempt.delete()

        messages.success(self.request, _('You have abandoned that task. Thank you for trying, and '
                                         'feel free to try again later!'))
        return redirect('users.profile.detail')


class FinishTaskView(UserProfileRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        task = self.get_object()
        attempt = get_object_or_404(TaskAttempt, user=self.request.user, task=task,
                                    state=TaskAttempt.STARTED)
        attempt.state = TaskAttempt.FINISHED
        attempt.save()

        return redirect('tasks.feedback', task.pk)


class CreateFeedbackView(UserProfileRequiredMixin, generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'tasks/feedback.html'

    def dispatch(self, request, *args, **kwargs):
        self.task = get_object_or_404(Task, pk=kwargs['pk'])
        return super(CreateFeedbackView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateFeedbackView, self).get_context_data(*args, **kwargs)
        ctx['task'] = self.task
        return ctx

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.user = self.request.user
        feedback.task = self.task
        feedback.save()

        messages.success(self.request, _('Your feedback has been submitted. Thanks!'))
        return redirect('users.profile.detail')
