# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.forms import ValidationError

from mock import Mock, patch
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.widgets import MyURLField


class MyURLFieldTests(TestCase):
    def test_clean_no_value(self):
        """
        If an empty string is passed into clean, then return None.
        """
        eq_(MyURLField().clean(''), None)

    def test_clean_valid_url_no_protocol(self):
        """
        If a valid url is passed into clean, but without a protocol,
        add http:// to the url and return it.
        """
        with patch('oneanddone.base.widgets.requests') as requests:
            requests.get.return_value = Mock(ok=True)
            eq_(MyURLField().clean('www.mozilla.org'), 'http://www.mozilla.org')

    def test_clean_valid_url_with_protocol(self):
        """
        If a valid url is passed into clean, with a protocol, return it.
        """
        with patch('oneanddone.base.widgets.requests') as requests:
            requests.get.return_value = Mock(ok=True)
        eq_(MyURLField().clean('https://www.mozilla.org'), 'https://www.mozilla.org')

    def test_clean_invalid_url(self):
        """
        If an invalid url is passed into clean, raise a ValidationError.
        """
        with self.assertRaises(ValidationError):
            with patch('oneanddone.base.widgets.requests') as requests:
                requests.get.return_value = Mock(ok=False)
                MyURLField().clean('www.mozilla.org.bad.url')
