# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.util import get_object_or_none


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
