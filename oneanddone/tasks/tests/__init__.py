from datetime import timedelta

from django.utils import timezone

from factory import DjangoModelFactory, fuzzy, Sequence, SubFactory

from oneanddone.tasks import models
from oneanddone.users.tests import UserFactory


class TaskProjectFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskProject

    name = Sequence(lambda n: 'test{0}'.format(n))
    creator = SubFactory(UserFactory)


class TaskTeamFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskTeam

    name = Sequence(lambda n: 'test{0}'.format(n))
    creator = SubFactory(UserFactory)


class TaskTypeFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskType

    name = Sequence(lambda n: 'test{0}'.format(n))
    creator = SubFactory(UserFactory)


class BugzillaBugFactory(DjangoModelFactory):
    FACTORY_FOR = models.BugzillaBug

    summary = Sequence(lambda n: 'test{0}'.format(n))
    bugzilla_id = Sequence(lambda n: n)


class TaskImportBatchFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskImportBatch

    description = Sequence(lambda n: 'test{0}'.format(n))
    query = Sequence(lambda n: 'test{0}'.format(n))
    source = models.TaskImportBatch.BUGZILLA
    creator = SubFactory(UserFactory)


class TaskInvalidationCriterionFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskInvalidationCriterion

    field_name = Sequence(lambda n: 'test{0}'.format(n))
    relation = models.TaskInvalidationCriterion.EQUAL
    field_value = Sequence(lambda n: 'test{0}'.format(n))
    creator = SubFactory(UserFactory)


class TaskFactory(DjangoModelFactory):
    FACTORY_FOR = models.Task

    name = Sequence(lambda n: 'test{0}'.format(n))
    short_description = Sequence(lambda n: 'test_description{0}'.format(n))
    instructions = Sequence(lambda n: 'test_instructions{0}'.format(n))
    execution_time = fuzzy.FuzzyChoice((15, 30, 45, 60))
    is_draft = False
    is_invalid = False
    creator = SubFactory(UserFactory)
    owner = creator
    project = SubFactory(TaskProjectFactory)
    team = SubFactory(TaskTeamFactory)
    type = SubFactory(TaskTypeFactory)
    repeatable = True
    priority = 3


class TaskAttemptFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskAttempt

    user = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
    state = models.TaskAttempt.STARTED
    requires_notification = False


class ValidTaskAttemptFactory(TaskAttemptFactory):
    """
    Creates task attempts where the created time is
    60 seconds before the current time.
    """

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(target_class)

        if cls.FACTORY_DJANGO_GET_OR_CREATE:
            attempt = cls._get_or_create(target_class, *args, **kwargs)
        else:
            attempt = manager.create(*args, **kwargs)

        attempt.created = timezone.now() + timedelta(seconds=-60)
        attempt.save()
        return attempt


class TaskKeywordFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskKeyword

    creator = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
    name = Sequence(lambda n: 'test{0}'.format(n))


class FeedbackFactory(DjangoModelFactory):
    FACTORY_FOR = models.Feedback

    attempt = SubFactory(TaskAttemptFactory)
    text = Sequence(lambda n: 'feedback{0}'.format(n))
