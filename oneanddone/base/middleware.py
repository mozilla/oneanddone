# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.utils import timezone


class TimezoneMiddleware(object):
    """
    Set the current timezone for all requests to be UTC.

    Will handle more complex timezone logic once we have more formal
    timezone support in the app.
    """
    def process_request(self, request):
        timezone.activate(timezone.utc)
