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


class TaskFactory(DjangoModelFactory):
    FACTORY_FOR = models.Task

    name = Sequence(lambda n: 'test{0}'.format(n))
    short_description = Sequence(lambda n: 'test_description{0}'.format(n))
    instructions = Sequence(lambda n: 'test_instructions{0}'.format(n))
    execution_time = fuzzy.FuzzyChoice((15, 30, 45, 60))
    is_draft = False
    creator = SubFactory(UserFactory)
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


class TaskKeywordFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskKeyword

    creator = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
    name = Sequence(lambda n: 'test{0}'.format(n))


class FeedbackFactory(DjangoModelFactory):
    FACTORY_FOR = models.Feedback

    attempt = SubFactory(TaskAttemptFactory)
    text = Sequence(lambda n: 'feedback{0}'.format(n))
