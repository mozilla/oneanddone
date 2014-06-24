# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.exceptions import PermissionDenied
from django.http import Http404

from oneanddone.tasks.models import Task


class TaskMustBeAvailableMixin(object):
    """
    Only allow published tasks to be listed, by filtering the
    queryset.
    """
    allow_expired_tasks = False

    def get_queryset(self):
        queryset = super(TaskMustBeAvailableMixin, self).get_queryset()
        return queryset.filter(Task.is_available_filter(allow_expired=self.allow_expired_tasks))


class HideNonRepeatableTaskMixin(object):
    """
    Do not allow access to a non-repeatable task that is not available to the user.
    """
    def get_object(self, queryset=None):
        task = super(HideNonRepeatableTaskMixin, self).get_object(queryset)
        if not task.is_available_to_user(self.request.user):
            raise Http404('Task unavailable.')
        return task


class APIRecordCreatorMixin(object):
    def pre_save(self, obj):
        obj.creator = self.request.user


class APIOnlyCreatorMayDeleteMixin(object):
    def pre_delete(self, obj):
        if obj.creator != self.request.user:
            raise PermissionDenied()
