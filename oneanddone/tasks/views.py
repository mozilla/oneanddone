# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from django_filters.views import FilterView
from rest_framework import generics
from tower import ugettext as _

from oneanddone.base.util import get_object_or_none
from oneanddone.tasks.filters import AvailableTasksFilterSet
from oneanddone.tasks.forms import FeedbackForm
from oneanddone.tasks.mixins import APIRecordCreatorMixin, APIOnlyCreatorMayDeleteMixin
from oneanddone.tasks.mixins import TaskMustBePublishedMixin
from oneanddone.tasks.models import Feedback, Task, TaskArea, TaskAttempt
from oneanddone.tasks.serializers import TaskSerializer, TaskAreaSerializer
from oneanddone.users.mixins import UserProfileRequiredMixin


class AvailableTasksView(TaskMustBePublishedMixin, FilterView):
    queryset = Task.objects.order_by('-execution_time')
    context_object_name = 'available_tasks'
    template_name = 'tasks/available.html'
    paginate_by = 10
    filterset_class = AvailableTasksFilterSet


class RandomTasksView(TaskMustBePublishedMixin, generic.ListView):
    queryset = Task.objects.order_by('?')
    template_name = 'tasks/random.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(RandomTasksView, self).get_context_data(*args, **kwargs)
        # Only return 5 tasks
        ctx['random_task_list'] = ctx['object_list'][:5]
        return ctx


class TaskDetailView(TaskMustBePublishedMixin, generic.DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    allow_expired_tasks = True

    def get_context_data(self, *args, **kwargs):
        ctx = super(TaskDetailView, self).get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated():
            ctx['attempt'] = get_object_or_none(TaskAttempt, user=self.request.user,
                                                task=self.object, state=TaskAttempt.STARTED)
        return ctx


class StartTaskView(UserProfileRequiredMixin, TaskMustBePublishedMixin,
                    generic.detail.SingleObjectMixin, generic.View):
    model = Task

    def post(self, *args, **kwargs):
        # Do not allow users to take more than one task at a time
        if self.request.user.attempts_in_progress.exists():
            messages.error(self.request, _('You may only work on one task at a time.'))
            return redirect('users.profile.detail')

        task = self.get_object()
        if not task.is_available:
            messages.error(self.request, _('That task is unavailable at this time.'))
            return redirect('tasks.available')

        attempt, created = TaskAttempt.objects.get_or_create(user=self.request.user, task=task,
                                                             state=TaskAttempt.STARTED)
        return redirect(task)


class TaskAttemptView(UserProfileRequiredMixin, generic.detail.SingleObjectMixin, generic.View):
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


class CreateFeedbackView(UserProfileRequiredMixin, TaskMustBePublishedMixin, generic.CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'tasks/feedback.html'

    def dispatch(self, request, *args, **kwargs):
        self.attempt = get_object_or_404(TaskAttempt, pk=kwargs['pk'], user=request.user,
                                         state__in=[TaskAttempt.FINISHED, TaskAttempt.ABANDONED])
        return super(CreateFeedbackView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(CreateFeedbackView, self).get_context_data(*args, **kwargs)
        ctx['attempt'] = self.attempt
        return ctx

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.attempt = self.attempt
        feedback.save()

        messages.success(self.request, _('Your feedback has been submitted. Thanks!'))
        return redirect('users.profile.detail')


class TaskListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailAPI(APIOnlyCreatorMayDeleteMixin,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskAreaListAPI(APIRecordCreatorMixin, generics.ListCreateAPIView):
    queryset = TaskArea.objects.all()
    serializer_class = TaskAreaSerializer


class TaskAreaDetailAPI(APIOnlyCreatorMayDeleteMixin,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskArea.objects.all()
    serializer_class = TaskAreaSerializer
