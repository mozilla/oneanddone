from factory import DjangoModelFactory, fuzzy, Sequence, SubFactory

from oneanddone.tasks import models
from oneanddone.users.tests import UserFactory


class TaskAreaFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskArea

    name = Sequence(lambda n: 'test{0}'.format(n))
    creator = SubFactory(UserFactory)


class TaskFactory(DjangoModelFactory):
    FACTORY_FOR = models.Task

    area = SubFactory(TaskAreaFactory)
    name = Sequence(lambda n: 'test{0}'.format(n))
    short_description = Sequence(lambda n: 'test_description{0}'.format(n))
    instructions = Sequence(lambda n: 'test_instructions{0}'.format(n))
    execution_time = fuzzy.FuzzyInteger(0, 60)
    is_draft = False
    creator = SubFactory(UserFactory)


class TaskAttemptFactory(DjangoModelFactory):
    FACTORY_FOR = models.TaskAttempt

    user = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
    state = models.TaskAttempt.STARTED


class FeedbackFactory(DjangoModelFactory):
    FACTORY_FOR = models.Feedback

    attempt = SubFactory(TaskAttemptFactory)
    text = Sequence(lambda n: 'feedback{0}'.format(n))
