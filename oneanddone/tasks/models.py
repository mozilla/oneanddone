# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import bleach
import jinja2
from markdown import markdown
from mptt.models import MPTTModel, TreeForeignKey

from oneanddone.base.models import CreatedModifiedModel


class TaskArea(MPTTModel, CreatedModifiedModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return ' > '.join(area.name for area in self.get_ancestors(include_self=True))

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

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    @property
    def is_available(self):
        """Whether this task is available for users to attempt."""
        now = timezone.now()
        return not (
            self.end_date and now > self.end_date or
            self.start_date and now < self.start_date
        )

    @property
    def instructions_html(self):
        """
        Return the instructions for a task after parsing them as
        markdown and bleaching/linkifying them.
        """
        linkified_instructions = bleach.linkify(self.instructions)
        html = markdown(linkified_instructions, output_format='html5')
        cleaned_html = bleach.clean(html, tags=settings.INSTRUCTIONS_ALLOWED_TAGS,
                                    attributes=settings.INSTRUCTIONS_ALLOWED_ATTRIBUTES)
        return jinja2.Markup(cleaned_html)

    @models.permalink
    def get_absolute_url(self):
        return ('tasks.detail', (self.id,))

    def __unicode__(self):
        return u'{area} > {name}'.format(area=self.area, name=self.name)

    # Help text
    instructions.help_text = """
        Markdown formatting is applied. See
        <a href="http://www.markdowntutorial.com/">http://www.markdowntutorial.com/</a> for a
        primer on Markdown syntax.
    """
    execution_time.help_text = """
        How many minutes will this take to finish?
    """
    start_date.help_text = """
        Date the task will start to be available. Task is immediately available if blank.
    """
    end_date.help_text = """
        If a task expires, it will not be shown to users regardless of whether it has been
        finished.
    """


class TaskAttempt(CreatedModifiedModel):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)

    STARTED = 0
    FINISHED = 1
    ABANDONED = 2
    state = models.IntegerField(default=STARTED, choices=(
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (ABANDONED, 'Abandoned')
    ))

    def __unicode__(self):
        return u'{user} attempt [{task}]'.format(user=self.user, task=self.task)


class Feedback(CreatedModifiedModel):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    text = models.TextField()

    def __unicode__(self):
        return u'Feedback: {user} for {task}'.format(user=self.user, task=self.task)
