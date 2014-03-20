# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.test.utils import override_settings

from mock import patch
from nose.tools import eq_

from oneanddone.base.helpers import less_css
from oneanddone.base.tests import TestCase


class LessCssTests(TestCase):
    @override_settings(TEMPLATE_DEBUG=False)
    def test_template_debug_false_call_css(self):
        """If TEMPLATE_DEBUG is false, call jingo_minify.helpers.css."""
        with patch('oneanddone.base.helpers.css') as mock_css:
            eq_(less_css('bundle'), mock_css.return_value)
            mock_css.assert_called_with('bundle')

    @override_settings(TEMPLATE_DEBUG=True)
    def test_template_debug_true_less_tags(self):
        """
        If TEMPLATE_DEBUG is true, return a set of link tags with
        stylesheet/less as the rel attribute.
        """
        with patch('oneanddone.base.helpers.get_css_urls') as get_css_urls:
            get_css_urls.return_value = ['foo', 'bar']
            output = less_css('bundle')
            get_css_urls.assert_called_with('bundle')

        self.assertHTMLEqual(output, """
            <link rel="stylesheet/less" media="screen,projection,tv" href="foo" />
            <link rel="stylesheet/less" media="screen,projection,tv" href="bar" />
        """)
