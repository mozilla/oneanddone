# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext as _


class ClosedTaskNotificationMiddleware(object):
    """
    Add messages to the request if required.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            for attempt in request.user.attempts_requiring_notification:
                messages.warning(request, _('The task that you were working on, "%s", '
                                            'has expired or become invalid '
                                            'and therefore has been closed.' % attempt.task.name),
                                 extra_tags='modal-message')
                attempt.requires_notification = False
                attempt.save()


class TimezoneMiddleware(object):
    """
    Set the current timezone for all requests to be UTC.

    Will handle more complex timezone logic once we have more formal
    timezone support in the app.
    """
    def process_request(self, request):
        timezone.activate(timezone.utc)
