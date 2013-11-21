# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from oneanddone.tasks.models import Task


class TaskMustBePublishedMixin(object):
    """Only allow published tasks to be accessed, by filtering the queryset."""
    def get_queryset(self):
        queryset = super(TaskMustBePublishedMixin, self).get_queryset()
        return queryset.filter(is_draft=False)
