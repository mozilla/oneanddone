# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.http import QueryDict

from mock import Mock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.util import get_object_or_none, SortHeaders


class GetObjectOrNoneTests(TestCase):
    def test_get(self):
        """
        If no exceptions are raised, return the value returned by
        Model.objects.get.
        """
        Model = Mock()
        eq_(get_object_or_none(Model, foo='bar'), Model.objects.get.return_value)
        Model.objects.get.assert_called_with(foo='bar')

    def test_none(self):
        """
        If a DoesNotExist or MultipleObjectsReturned exception is
        raised, return None.
        """
        Model = Mock(DoesNotExist=Exception, MultipleObjectsReturned=Exception)
        Model.objects.get.side_effect = Model.DoesNotExist
        eq_(get_object_or_none(Model, foo='bar'), None)

        Model.objects.get.side_effect = Model.MultipleObjectsReturned
        eq_(get_object_or_none(Model, foo='bar'), None)


class GetSortHeaders(TestCase):
    def setUp(self):
        self.header_list = (
            ('Title 1', 'field_1'),
            ('Title 2', 'field_2', 'Long Title 2')
        )

    def test_headers_default(self):
        """
        If no related query params exist, the first column is sorted ascending.
        """
        request = Mock(GET=QueryDict(''))
        sort_headers = SortHeaders(request, self.header_list)
        headers = list(sort_headers.headers())
        eq_(headers[0], {
            'url': '&ot=desc&o=0',
            'text': 'Title 1',
            'title': 'Title 1',
            'class_attr': {'class': 'orderable sorted asc'},
            'sortable': True})
        eq_(headers[1], {
            'url': '&ot=asc&o=1',
            'text': 'Title 2',
            'title': 'Long Title 2',
            'class_attr': {'class': 'orderable'},
            'sortable': True})

    def test_headers_col1_desc(self):
        """
        If the first column is sorted desc, set it up to be sorted asc.
        """
        request = Mock(GET=QueryDict('ot=desc&o=0'))
        sort_headers = SortHeaders(request, self.header_list)
        headers = list(sort_headers.headers())
        eq_(headers[0], {
            'url': '&ot=asc&o=0',
            'text': 'Title 1',
            'title': 'Title 1',
            'class_attr': {'class': 'orderable sorted desc'},
            'sortable': True})
        eq_(headers[1], {
            'url': '&ot=asc&o=1',
            'text': 'Title 2',
            'title': 'Long Title 2',
            'class_attr': {'class': 'orderable'},
            'sortable': True})

    def test_headers_col2_asc(self):
        """
        If the second column is sorted asc, set it up to be sorted desc.
        """
        request = Mock(GET=QueryDict('ot=asc&o=1'))
        sort_headers = SortHeaders(request, self.header_list)
        headers = list(sort_headers.headers())
        eq_(headers[0], {
            'url': '&ot=asc&o=0',
            'text': 'Title 1',
            'title': 'Title 1',
            'class_attr': {'class': 'orderable'},
            'sortable': True})
        eq_(headers[1], {
            'url': '&ot=desc&o=1',
            'text': 'Title 2',
            'title': 'Long Title 2',
            'class_attr': {'class': 'orderable sorted asc'},
            'sortable': True})

    def test_get_order_by_default(self):
        """
        Default order by is first field ascending.
        """
        request = Mock(GET=QueryDict(''))
        sort_headers = SortHeaders(request, self.header_list)
        eq_(sort_headers.get_order_by(), 'field_1')

    def test_get_order_by_col1_desc(self):
        """
        If first field descending is selected, return first field name
        with a minus sign.
        """
        request = Mock(GET=QueryDict('ot=desc&o=0'))
        sort_headers = SortHeaders(request, self.header_list)
        eq_(sort_headers.get_order_by(), '-field_1')

    def test_get_order_by_col2_asc(self):
        """
        If second field ascending is selected, return second field name
        without a minus sign.
        """
        request = Mock(GET=QueryDict('ot=asc&o=1'))
        sort_headers = SortHeaders(request, self.header_list)
        eq_(sort_headers.get_order_by(), 'field_2')
