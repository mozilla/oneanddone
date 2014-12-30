# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

import bleach
import jinja2
from markdown import markdown
from tower import ugettext as _

from oneanddone.base.models import CachedModel, CreatedByModel, CreatedModifiedModel
from oneanddone.tasks.bugzilla_utils import BugzillaUtils


class BugzillaBug(models.Model):
    bugzilla_id = models.IntegerField(max_length=20, unique=True)
    summary = models.CharField(max_length=255)
    tasks = generic.GenericRelation('Task')

    def __unicode__(self):
        return ' '.join(['Bug', str(self.bugzilla_id)])


class Feedback(CachedModel, CreatedModifiedModel):
    attempt = models.OneToOneField('TaskAttempt')
    text = models.TextField()

    def __unicode__(self):
        return u'Feedback: {user} for {task}'.format(
            user=self.attempt.user, task=self.attempt.task)


class TaskAttempt(CachedModel, CreatedModifiedModel):
    task = models.ForeignKey('Task', related_name='taskattempt_set')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    STARTED = 0
    FINISHED = 1
    ABANDONED = 2
    CLOSED = 3

    requires_notification = models.BooleanField(default=False)
    state = models.IntegerField(default=STARTED, choices=(
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (ABANDONED, 'Abandoned'),
        (CLOSED, 'Closed')
    ))

    @property
    def attempts_by_same_user(self):
        if self.user:
            return self.user.taskattempt_set.all()
        return TaskAttempt.objects.none()

    @property
    def attempt_length_in_minutes(self):
        start_seconds = time.mktime(self.created.timetuple())
        end_seconds = time.mktime(self.modified.timetuple())
        return round((end_seconds - start_seconds) / 60, 1)

    @property
    def feedback_display(self):
        if self.has_feedback:
            return self.feedback.text
        return _('No feedback for this attempt')

    @property
    def has_feedback(self):
        try:
            self.feedback
            return True
        except Feedback.DoesNotExist:
            return False

    @property
    def next_task(self):
        return self.task.next_task

    @classmethod
    def close_expired_task_attempts(self):
        """
        Close any attempts for tasks that have expired
        """
        open_attempts = self.objects.filter(state=self.STARTED)
        closed = 0
        for attempt in open_attempts:
            if not attempt.task.is_available:
                attempt.state = self.CLOSED
                attempt.requires_notification = True
                attempt.save()
                closed += 1
        return closed

    @classmethod
    def close_stale_onetime_attempts(self):
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

    def __unicode__(self):
        return u'{user} attempt [{task}]'.format(user=self.user, task=self.task)

    class Meta(CreatedModifiedModel.Meta):
        ordering = ['-modified']


class TaskKeyword(CachedModel, CreatedModifiedModel, CreatedByModel):
    task = models.ForeignKey('Task', related_name='keyword_set')

    name = models.CharField(max_length=255, verbose_name='keyword')

    def __unicode__(self):
        return self.name


class TaskImportBatch(CreatedModifiedModel, CreatedByModel):
    """
        Set of Tasks created in one step based on an external search query.
        One Task is created per query result.
    """
    BUGZILLA = 0
    OTHER = 1

    description = models.CharField(max_length=255,
                                   verbose_name='batch summary')
    query = models.TextField(verbose_name='query URL')
    # other sources might be Moztrap, etc.
    source = models.IntegerField(
        choices=(
            (BUGZILLA, 'Bugzilla@Mozilla'),
            (OTHER, 'Other')
        ),
        default=BUGZILLA)

    def __unicode__(self):
        return self.description

    query.help_text = """
        The URL to the Bugzilla@Mozilla search query that yields the items you
        want to create tasks from.
    """
    description.help_text = """
        A summary of what items are being imported.
    """


class TaskInvalidationCriterion(CreatedModifiedModel, CreatedByModel):
    """
    Condition that should cause a Task to become invalid.
    """
    batches = models.ManyToManyField('TaskImportBatch')

    EQUAL = 0
    NOT_EQUAL = 1
    choices = {EQUAL: '==', NOT_EQUAL: '!='}

    field_name = models.CharField(max_length=80)
    field_value = models.CharField(max_length=80)
    relation = models.IntegerField(choices=choices.items(),
                                   default=EQUAL)

    def passes(self, bug):
        sought_value = self.field_value.lower()
        actual_value = bug[self.field_name.lower()].lower()
        matches = sought_value == actual_value
        if ((self.relation == self.EQUAL and matches) or
                (self.relation == self.NOT_EQUAL and not matches)):
            return True
        return False

    def __unicode__(self):
        return ' '.join([str(self.field_name),
                         self.choices[self.relation],
                         self.field_value])

    class Meta(CreatedModifiedModel.Meta):
        verbose_name_plural = "task invalidation criteria"

    field_name.help_text = """
        Name of field recognized by Bugzilla@Mozilla REST API. Examples:
        status, resolution, component.
    """
    field_value.help_text = """
        Target value of the field to be checked.
    """
    relation.help_text = """
        Relationship (equality/inequality) between name and value.
    """


class TaskMetrics(CreatedModifiedModel):
    task = models.OneToOneField('Task')
    abandoned_users = models.IntegerField(null=True, blank=True)
    closed_users = models.IntegerField(null=True, blank=True)
    completed_users = models.IntegerField(null=True, blank=True)
    incomplete_users = models.IntegerField(null=True, blank=True)
    user_completes_then_completes_another_count = models.IntegerField(null=True, blank=True)
    user_completes_then_takes_another_count = models.IntegerField(null=True, blank=True)
    user_takes_then_quits_count = models.IntegerField(null=True, blank=True)
    too_short_completed_attempts_count = models.IntegerField(null=True, blank=True)

    @classmethod
    def get_medians(cls):
        metrics = cls.objects.all()
        medians = {}
        for metric in ('abandoned_users', 'closed_users', 'completed_users',
                       'incomplete_users',
                       'user_completes_then_completes_another_count',
                       'user_completes_then_takes_another_count',
                       'user_takes_then_quits_count',
                       'too_short_completed_attempts_count'):
            medians[metric] = cls.median_value(metrics, metric)
        return medians

    @classmethod
    def median_value(cls, queryset, term):
        count = queryset.count()
        return queryset.values_list(term, flat=True).order_by(term)[int(round(count / 2))]

    @classmethod
    def get_averages(cls):
        return cls.objects.aggregate(
            avg_abandoned_users=Avg('abandoned_users'),
            avg_closed_users=Avg('closed_users'),
            avg_completed_users=Avg('completed_users'),
            avg_incomplete_users=Avg('incomplete_users'),
            avg_user_completes_then_completes_another_count=Avg('user_completes_then_completes_another_count'),
            avg_user_completes_then_takes_another_count=Avg('user_completes_then_takes_another_count'),
            avg_user_takes_then_quits_count=Avg('user_takes_then_quits_count'),
            avg_too_short_completed_attempts_count=Avg('too_short_completed_attempts_count'))

    @classmethod
    def update_task_metrics(cls, force_update=False):
        """
        Background routine to update the task metrics
        """
        HOURS_BETWEEN_UPDATES = 5.5
        timestamp_of_last_update = timezone.now() - timedelta(hours=HOURS_BETWEEN_UPDATES)
        if force_update:
            tasks_to_update = Task.objects.all()
        else:
            tasks_to_update = Task.objects.filter(taskattempt_set__modified__gte=timestamp_of_last_update)
        for task in tasks_to_update:
            metrics, created = cls.objects.get_or_create(task=task)
            metrics.abandoned_users = task.abandoned_user_count
            metrics.closed_users = task.closed_user_count
            metrics.completed_users = task.completed_user_count
            metrics.incomplete_users = task.incomplete_user_count
            metrics.too_short_completed_attempts_count = task.too_short_completed_attempts.count()
            # Count times that users completed this task and then went on to
            # take or complete another task
            completes_then_completes_users = set()
            completes_then_takes_users = set()
            for attempt in task.completed_attempts:
                if attempt.attempts_by_same_user.filter(
                        created__gt=attempt.modified).exists():
                    completes_then_takes_users.add(attempt.user)
                if attempt.attempts_by_same_user.filter(
                        state=TaskAttempt.FINISHED,
                        created__gt=attempt.modified).exists():
                    completes_then_completes_users.add(attempt.user)
            # Count times that users took this task and then did not
            # go on to another task
            takes_then_leaves_users = set()
            for attempt in task.all_attempts:
                if not (attempt.attempts_by_same_user
                        .filter(created__gt=attempt.modified).exists()):
                    takes_then_leaves_users.add(attempt.user)
            metrics.user_completes_then_completes_another_count = len(completes_then_completes_users)
            metrics.user_completes_then_takes_another_count = len(completes_then_takes_users)
            metrics.user_takes_then_quits_count = len(takes_then_leaves_users)
            metrics.save()
        return len(tasks_to_update)

    class Meta():
        ordering = ['-completed_users']


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

    batch = models.ForeignKey(TaskImportBatch, blank=True, null=True)
    # imported_item may be BugzillaBug for now. In future, other sources such
    # as Moztrap may be possible
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    imported_item = generic.GenericForeignKey('content_type', 'object_id')
    next_task = models.ForeignKey('Task', null=True, blank=True, related_name='previous_task')
    owner = models.ForeignKey(User, related_name='owner')
    project = models.ForeignKey(TaskProject, blank=True, null=True)
    team = models.ForeignKey(TaskTeam)
    type = models.ForeignKey(TaskType, blank=True, null=True)

    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    P1 = 1
    P2 = 2
    P3 = 3

    difficulty = models.IntegerField(
        choices=(
            (BEGINNER, 'Beginner'),
            (INTERMEDIATE, 'Intermediate'),
            (ADVANCED, 'Advanced')
        ),
        default=BEGINNER,
        verbose_name='task difficulty')
    end_date = models.DateTimeField(blank=True, null=True)
    execution_time = models.IntegerField(
        choices=((i, i) for i in (15, 30, 45, 60)),
        blank=False,
        default=30,
        verbose_name='estimated time'
    )
    instructions = models.TextField()
    is_draft = models.BooleanField(verbose_name='draft')
    is_invalid = models.BooleanField(verbose_name='invalid')
    name = models.CharField(max_length=255, verbose_name='title', unique=True)
    prerequisites = models.TextField(blank=True)
    priority = models.IntegerField(
        choices=(
            (P1, 'P1'),
            (P2, 'P2'),
            (P3, 'P3')
        ),
        default=P3,
        verbose_name='task priority')
    repeatable = models.BooleanField(default=True)
    short_description = models.CharField(blank=True, null=True, max_length=255, verbose_name='description')
    start_date = models.DateTimeField(blank=True, null=True)
    why_this_matters = models.TextField(blank=True)

    @property
    def abandoned_attempts(self):
        return self.taskattempt_set.filter(state=TaskAttempt.ABANDONED)

    @property
    def abandoned_user_count(self):
        qs = self.abandoned_attempts.values('task').annotate(
            user_count=Count('user', distinct=True))
        if qs:
            return qs[0]['user_count']
        return 0

    @property
    def all_attempts(self):
        return self.taskattempt_set.all()

    @property
    def bugzilla_bug(self):
        if self.has_bugzilla_bug:
            return BugzillaUtils().request_bug(self.imported_item.bugzilla_id)
        return None

    @property
    def closed_attempts(self):
        return self.taskattempt_set.filter(state=TaskAttempt.CLOSED)

    @property
    def closed_user_count(self):
        qs = self.closed_attempts.values('task').annotate(
            user_count=Count('user', distinct=True))
        if qs:
            return qs[0]['user_count']
        return 0

    @property
    def completed_attempts(self):

        return self.taskattempt_set.filter(
            modified__gt=F('created') + timedelta(seconds=settings.MIN_DURATION_FOR_COMPLETED_ATTEMPTS),
            state=TaskAttempt.FINISHED)

    @property
    def completed_user_count(self):
        qs = self.completed_attempts.values('task').annotate(
            user_count=Count('user', distinct=True))
        if qs:
            return qs[0]['user_count']
        return 0

    @property
    def first_previous_task(self):
        previous_tasks = self.previous_task.all().order_by('created')
        if len(previous_tasks):
            return previous_tasks[0]
        return None

    @property
    def has_bugzilla_bug(self):
        return isinstance(self.imported_item, BugzillaBug)

    @property
    def incomplete_attempts(self):
        return self.taskattempt_set.exclude(state=TaskAttempt.FINISHED)

    @property
    def incomplete_user_count(self):
        qs = self.incomplete_attempts.values('task').annotate(
            user_count=Count('user', distinct=True))
        if qs:
            return qs[0]['user_count']
        return 0

    @property
    def instructions_html(self):
        return self._yield_html(self.instructions)

    @property
    def invalidation_criteria(self):
        if self.batch:
            return self.batch.taskinvalidationcriterion_set.all()
        return None

    @property
    def is_available(self):
        """Whether this task is available for users to attempt."""
        if self.is_draft or self.is_invalid:
            return False

        now = timezone.now()
        return not (
            (self.end_date and now > self.end_date) or
            (self.start_date and now < self.start_date)
        )

    @property
    def is_completed(self):
        return (not self.repeatable and
                self.taskattempt_set.filter(
                    state=TaskAttempt.FINISHED).exists())

    @property
    def is_taken(self):
        return (not self.repeatable and
                self.taskattempt_set.filter(
                    state=TaskAttempt.STARTED).exists())

    @property
    def keywords_list(self):
        return ', '.join([keyword.name for keyword in self.keyword_set.all()])

    @property
    def prerequisites_html(self):
        return self._yield_html(self.prerequisites)

    @property
    def too_short_completed_attempts(self):
        return self.taskattempt_set.filter(
            modified__lte=F('created') + timedelta(seconds=settings.MIN_DURATION_FOR_COMPLETED_ATTEMPTS),
            state=TaskAttempt.FINISHED)

    @property
    def why_this_matters_html(self):
        return self._yield_html(self.why_this_matters)

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

    def get_absolute_url(self):
        return reverse('tasks.detail', args=[self.id])

    def get_edit_url(self):
        return reverse('tasks.edit', args=[self.id])

    def get_next_task_url(self):
        if self.next_task:
            return reverse('tasks.detail', args=[self.next_task.id])
        return ''

    def get_clone_url(self):
        return reverse('tasks.clone', args=[self.id])

    def is_available_to_user(self, user):
        repeatable_filter = Q(~Q(user=user) & ~Q(state=TaskAttempt.ABANDONED))
        return self.is_available and (
            self.repeatable or not self.taskattempt_set.filter(repeatable_filter).exists())

    def replace_keywords(self, keywords, creator):
        self.keyword_set.all().delete()
        for keyword in keywords:
            if len(keyword):
                self.keyword_set.create(name=keyword, creator=creator)

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if not self.is_available:
            # Close any open attempts
            self.taskattempt_set.filter(state=TaskAttempt.STARTED).update(
                state=TaskAttempt.CLOSED,
                requires_notification=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def invalidate_tasks(self):
        """
        Invalidate any tasks for which invalidation criteria is met
        """
        bugzillabug_type = ContentType.objects.get(model="BugzillaBug")
        tasks = self.objects.filter(
            is_invalid=False,
            content_type=bugzillabug_type)
        invalidated = 0
        for task in tasks:
            bug = task.bugzilla_bug
            for criterion in task.invalidation_criteria:
                if criterion.passes(bug):
                    task.is_invalid = True
                    task.save()
                    invalidated += 1
        return invalidated

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
        # Use just the date to allow caching
        now = now.replace(hour=0, minute=0, second=0)
        q_filter = (pQ(is_draft=False) & pQ(is_invalid=False) &
                    (pQ(start_date__isnull=True) | pQ(start_date__lte=now)))

        if not allow_expired:
            q_filter = q_filter & (pQ(end_date__isnull=True) | pQ(end_date__gt=now))

        q_filter = q_filter & (
            pQ(repeatable=True) | (
                ~pQ(taskattempt_set__state=TaskAttempt.STARTED) &
                ~pQ(taskattempt_set__state=TaskAttempt.FINISHED)))

        return q_filter

    def __unicode__(self):
        return self.name

    class Meta(CreatedModifiedModel.Meta):
        ordering = ['priority', 'difficulty']
