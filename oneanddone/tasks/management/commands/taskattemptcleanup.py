# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.core.management.base import BaseCommand

from oneanddone.tasks.models import TaskAttempt


class Command(BaseCommand):
    help = 'Cleans up status of task attempts based on task data'

    def handle(self, *args, **options):
        closed = TaskAttempt.close_stale_onetime_attempts()
        self.stdout.write('%s stale one-time attempts were closed\n' % closed)
        closed = TaskAttempt.close_expired_task_attempts()
        self.stdout.write('%s attempts for expired tasks were closed\n' % closed)
