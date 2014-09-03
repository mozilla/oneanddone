# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime

from django.utils import timezone

from mock import Mock, patch
from nose.tools import ok_

from oneanddone.base.tests import TestCase
from oneanddone.base.filters import MyDateRangeFilter


def aware_datetime(*args, **kwargs):
    return timezone.make_aware(datetime(*args, **kwargs), timezone.utc)


class MyDateRangeFilterTests(TestCase):
    def test_filter_with_start(self):
        """
        filter should apply a range test using the start value and the current
        date if only a start is passed.
        """
        mdrf = MyDateRangeFilter()
        mdrf.name = 'test_field'
        qs = Mock()
        value = slice(1, None)
        with patch('oneanddone.base.filters.timezone.now') as now:
            now.return_value = aware_datetime(2013, 12, 1)
            mdrf.filter(qs, value)
            qs.filter.assert_called_with(test_field__range=(1, now.return_value))

    def test_filter_with_end(self):
        """
        filter should apply a range test using 2013, 1, 1 and the stop value
        if only a stop is passed.
        """
        mdrf = MyDateRangeFilter()
        mdrf.name = 'test_field'
        qs = Mock()
        value = slice(None, 2)
        mdrf.filter(qs, value)
        qs.filter.assert_called_with(
            test_field__range=(
                timezone.make_aware(datetime(2013, 1, 1), timezone.utc),
                2))

    def test_filter_with_none(self):
        """
        filter should not call filter on the queryset if None is
        passed as the value.
        """
        mdrf = MyDateRangeFilter()
        qs = Mock()
        value = None
        mdrf.filter(qs, value)
        ok_(not qs.filter.called)
