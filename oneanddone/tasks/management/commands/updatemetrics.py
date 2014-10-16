# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from oneanddone.tasks.models import TaskMetrics


class Command(BaseCommand):
    help = 'Updates stored metrics'
    option_list = BaseCommand.option_list + (
        make_option('--force_update',
                    action='store_true',
                    dest='force_update',
                    default=False,
                    help='Force updating of all tasks'),)

    def handle(self, *args, **options):
        updated = TaskMetrics.update_task_metrics(force_update=options['force_update'])
        self.stdout.write('%s: %s tasks had their metrics updated\n' %
                          (datetime.now().isoformat(), updated))
