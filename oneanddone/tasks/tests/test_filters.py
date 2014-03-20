# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.filters import AvailableTasksFilterSet, TreeFilter
from oneanddone.tasks.models import TaskArea
from oneanddone.tasks.tests import TaskAreaFactory, TaskFactory


class TreeFilterTests(TestCase):
    def test_filter(self):
        """
        Filter should match objects that are related to the given value
        or it's descendants via the field specified in the filter name.
        """
        # root -> child1 -> grandchild1 -> great_grandchild1
        #     \-> child2
        root = TaskAreaFactory.create()
        child1, child2 = TaskAreaFactory.create_batch(2, parent=root)
        grandchild1 = TaskAreaFactory.create(parent=child1)
        great_grandchild1 = TaskAreaFactory.create(parent=grandchild1)

        # Should match all areas "below" child1.
        tree_filter = TreeFilter(name='parent')
        areas = tree_filter.filter(TaskArea.objects.all(), child1)
        eq_(set(areas), set([grandchild1, great_grandchild1]))


class AvailableTasksFilterSetTests(TestCase):
    def test_area_filter_only_with_available_tasks(self):
        """
        Only TaskAreas with available tasks and their parents should be
        included in the area filter.
        """
        # root -> child1 -> grandchild1
        #     \-> child2
        root = TaskAreaFactory.create()
        child1, child2 = TaskAreaFactory.create_batch(2, parent=root)
        grandchild1 = TaskAreaFactory.create(parent=child1)

        # Only grandchild1 has available tasks.
        TaskFactory.create(area=grandchild1, is_draft=False)

        # Area should include grandlchild1 and its parents.
        filter_set = AvailableTasksFilterSet()
        areas = filter_set.filters['area'].extra['queryset']
        eq_(set(areas), set([root, child1, grandchild1]))

    def test_area_filter_empty_children(self):
        """
        If a TaskArea has available tasks but its children don't, the
        children should not be included in the area filter.
        """
        # root -> child1 -> grandchild1
        #     \-> child2
        root = TaskAreaFactory.create()
        child1, child2 = TaskAreaFactory.create_batch(2, parent=root)
        grandchild1 = TaskAreaFactory.create(parent=child1)

        # Only child1 has available tasks.
        TaskFactory.create(area=child1, is_draft=False)

        # Area should include child1, but not grandchild1.
        filter_set = AvailableTasksFilterSet()
        areas = filter_set.filters['area'].extra['queryset']
        eq_(set(areas), set([root, child1]))
