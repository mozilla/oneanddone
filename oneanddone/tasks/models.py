# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey

from oneanddone.base.models import CreatedModifiedModel


class TaskArea(MPTTModel, CreatedModifiedModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Task(CreatedModifiedModel):
    """
    Task for a user to attempt to fulfill. Tasks are categorized by area
    and include instructions and estimated execution times. Certain
    tasks can also be completed multiple times.
    """
    area = TreeForeignKey(TaskArea)

    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    instructions = models.TextField()

    execution_time = models.IntegerField()
    allow_multiple_finishes = models.BooleanField(
        default=False, help_text=('If allowed, the task will remain available until it expires, '
                                  'instead of being taken down once an attempt is finished.'))

    start_date = models.DateTimeField(
        blank=True, null=True, help_text=('Date the task will start to be available. Task is '
                                          'immediately available if blank.'))
    end_date = models.DateTimeField(
        blank=True, null=True, help_text=('If a task expires, it will not be shown to users '
                                          'regardless of if it has been finished.'))

    @property
    def is_available(self):
        """Whether this task is available for users to attempt."""
        now = timezone.now()
        if self.end_date and now > self.end_date:
            return False
        elif self.start_date and now < self.start_date:
            return False
        else:
            return (self.allow_multiple_finishes or
                    not self.taskattempt_set.filter(state=TaskAttempt.FINISHED).exists())

    @models.permalink
    def get_absolute_url(self):
        return ('tasks.detail', (self.id,))

    def __unicode__(self):
        return u'{area} > {name}'.format(area=self.area, name=self.name)


class TaskAttempt(CreatedModifiedModel):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)

    STARTED = 0
    FINISHED = 1
    state = models.IntegerField(default=STARTED, choices=(
        (STARTED, 'Started'),
        (FINISHED, 'Finished')
    ))

    def __unicode__(self):
        return u'{user} attempt [{task}]'.format(user=self.user, task=self.task)


class Feedback(CreatedModifiedModel):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    text = models.TextField()

    def __unicode__(self):
        return u'Feedback: {user} for {task}'.format(user=self.user, task=self.task)
