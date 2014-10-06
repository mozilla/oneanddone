# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.core.management.base import BaseCommand

from oneanddone.tasks.models import Task, TaskAttempt


class Command(BaseCommand):
    help = 'Cleans up status of tasks and attempts based on task data'

    def handle(self, *args, **options):
        invalidated = Task.invalidate_tasks()
        self.stdout.write('%s: %s tasks were invalidated via bug data\n' %
                          (datetime.now().isoformat(), invalidated))
        closed = TaskAttempt.close_stale_onetime_attempts()
        self.stdout.write('%s: %s stale one-time attempts were closed\n' %
                          (datetime.now().isoformat(), closed))
        closed = TaskAttempt.close_expired_task_attempts()
        self.stdout.write('%s: %s attempts for expired tasks were closed\n' %
                          (datetime.now().isoformat(), closed))
