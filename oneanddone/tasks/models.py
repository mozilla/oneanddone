# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone

import bleach
import jinja2
from markdown import markdown

from oneanddone.base.models import CachedModel, CreatedByModel, CreatedModifiedModel


class TaskProject(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaskTeam(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TaskType(CachedModel, CreatedModifiedModel, CreatedByModel):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Task(CachedModel, CreatedModifiedModel, CreatedByModel):
    """
    Task for a user to attempt to fulfill.
    """

    class Meta(CreatedModifiedModel.Meta):
        ordering = ['priority', 'difficulty']

    project = models.ForeignKey(TaskProject, blank=True, null=True)
    team = models.ForeignKey(TaskTeam)
    type = models.ForeignKey(TaskType, blank=True, null=True)

    EASY = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    difficulty = models.IntegerField(
        choices=(
            (EASY, 'Easy'),
            (INTERMEDIATE, 'Intermediate'),
            (ADVANCED, 'Advanced')
        ),
        default=EASY,
        verbose_name='task difficulty')
    P1 = 1
    P2 = 2
    P3 = 3
    priority = models.IntegerField(
        choices=(
            (P1, 'P1'),
            (P2, 'P2'),
            (P3, 'P3')
        ),
        default=P3,
        verbose_name='task priority')
    end_date = models.DateTimeField(blank=True, null=True)
    execution_time = models.IntegerField(
        choices=((i, i) for i in (15, 30, 45, 60)),
        blank=False,
        default=30,
        verbose_name='estimated time'
    )
    instructions = models.TextField()
    is_draft = models.BooleanField(verbose_name='draft?')
    name = models.CharField(max_length=255, verbose_name='title')
    prerequisites = models.TextField(blank=True)
    repeatable = models.BooleanField(default=True)
    short_description = models.CharField(max_length=255, verbose_name='description')
    start_date = models.DateTimeField(blank=True, null=True)
    why_this_matters = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if not self.is_available:
            # Close any open attempts
            self.taskattempt_set.filter(state=TaskAttempt.STARTED).update(
                state=TaskAttempt.CLOSED,
                requires_notification=True)

    def _yield_html(self, field):
        """
        Return the requested field for a task after parsing them as
        markdown and bleaching/linkifying them.
        """
        linkified_field = bleach.linkify(field, parse_email=True)
        html = markdown(linkified_field, output_format='html5')
        cleaned_html = bleach.clean(html, tags=settings.INSTRUCTIONS_ALLOWED_TAGS,
                                    attributes=settings.INSTRUCTIONS_ALLOWED_ATTRIBUTES)
        return jinja2.Markup(cleaned_html)

    @property
    def keywords_list(self):
        return ', '.join([keyword.name for keyword in self.keyword_set.all()])

    @property
    def is_available(self):
        """Whether this task is available for users to attempt."""
        if self.is_draft:
            return False

        now = timezone.now()
        return not (
            (self.end_date and now > self.end_date) or
            (self.start_date and now < self.start_date)
        )

    def is_available_to_user(self, user):
        repeatable_filter = Q(~Q(user=user) & ~Q(state=TaskAttempt.ABANDONED))
        return self.is_available and (
            self.repeatable or not self.taskattempt_set.filter(repeatable_filter).exists())

    @property
    def is_taken(self):
        return not self.repeatable and self.taskattempt_set.filter(state=TaskAttempt.STARTED).exists()

    @property
    def is_completed(self):
        return not self.repeatable and self.taskattempt_set.filter(state=TaskAttempt.FINISHED).exists()

    @property
    def instructions_html(self):
        return self._yield_html(self.instructions)

    @property
    def prerequisites_html(self):
        return self._yield_html(self.prerequisites)

    @property
    def why_this_matters_html(self):
        return self._yield_html(self.why_this_matters)

    def get_absolute_url(self):
        return reverse('tasks.detail', args=[self.id])

    def get_edit_url(self):
        return reverse('tasks.edit', args=[self.id])

    def __unicode__(self):
        return self.name

    @classmethod
    def is_available_filter(self, now=None, allow_expired=False, prefix=''):
        """
        Return a Q object (queryset filter) that matches available
        tasks.

        :param now:
            Datetime to use as the current datetime. Defaults to
            django.utils.timezone.now().

        :param allow_expired:
            If False, exclude tasks past their end date.

        :param prefix:
            Prefix to use for queryset filter names. Good for when you
            want to filter on a related tasks and need 'task__'
            prepended to the filters.
        """
        # Convenient shorthand for creating a Q filter with the prefix.
        pQ = lambda **kwargs: Q(**dict((prefix + key, value) for key, value in kwargs.items()))

        now = now or timezone.now()
        now = now.replace(hour=0, minute=0, second=0)  # Use just the date to allow caching
        q_filter = pQ(is_draft=False) & (pQ(start_date__isnull=True) | pQ(start_date__lte=now))

        if not allow_expired:
            q_filter = q_filter & (pQ(end_date__isnull=True) | pQ(end_date__gt=now))

        q_filter = q_filter & (
            pQ(repeatable=True) | (
                ~pQ(taskattempt_set__state=TaskAttempt.STARTED) &
                ~pQ(taskattempt_set__state=TaskAttempt.FINISHED)))

        return q_filter

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
    is_draft.help_text = """
        If you do not wish to publish the task yet, set it as a draft. Draft tasks will not
        be viewable by contributors.
    """


class TaskKeyword(CachedModel, CreatedModifiedModel, CreatedByModel):
    task = models.ForeignKey(Task, related_name='keyword_set')

    name = models.CharField(max_length=255, verbose_name='keyword')

    def __unicode__(self):
        return self.name


class TaskAttempt(CachedModel, CreatedModifiedModel):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, related_name='taskattempt_set')

    STARTED = 0
    FINISHED = 1
    ABANDONED = 2
    CLOSED = 3
    state = models.IntegerField(default=STARTED, choices=(
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (ABANDONED, 'Abandoned'),
        (CLOSED, 'Closed')
    ))
    requires_notification = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{user} attempt [{task}]'.format(user=self.user, task=self.task)

    class Meta(CreatedModifiedModel.Meta):
        ordering = ['-modified']

    @classmethod
    def close_expired_onetime_attempts(self):
        """
        Close any attempts for one-time tasks that have been open for over 30 days
        """
        compare_date = timezone.now() - timedelta(days=settings.TASK_ATTEMPT_EXPIRATION_DURATION)
        expired_onetime_attempts = self.objects.filter(
            state=self.STARTED,
            created__lte=compare_date,
            task__repeatable=False)
        return expired_onetime_attempts.update(
            state=self.CLOSED,
            requires_notification=True)


class Feedback(CachedModel, CreatedModifiedModel):
    attempt = models.ForeignKey(TaskAttempt)
    text = models.TextField()

    def __unicode__(self):
        return u'Feedback: {user} for {task}'.format(
            user=self.attempt.user, task=self.attempt.task)
