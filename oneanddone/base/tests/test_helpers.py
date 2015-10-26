# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import urlparse

from django.http import QueryDict
from mock import Mock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.base.templatetags.jinja_helpers import page_url, buglinkify


class PageUrlTests(TestCase):
    def test_basic(self):
        """
        page_url should return a relative link to the current page,
        preserving the GET arguments from the given request, and adding
        a page parameter for the given page.
        """

        request = Mock(GET=QueryDict('foo=bar&baz=5'))
        url = urlparse.urlsplit(page_url(request, 4))
        args = urlparse.parse_qs(url.query)
        eq_(args, {'foo': ['bar'], 'baz': ['5'], 'page': ['4']})

    def test_existing_page_arg(self):
        """
        If the current page already has a page GET argument, override
        it.
        """
        request = Mock(GET=QueryDict('foo=bar&page=5'))
        url = urlparse.urlsplit(page_url(request, 4))
        args = urlparse.parse_qs(url.query)
        eq_(args, {'foo': ['bar'], 'page': ['4']})

    def test_repeats(self):
        """
        GET parameters with multiple values should have all their
        values preserved
        """
        request = Mock(GET=QueryDict('foo=bar&baz=5&foo=ok'))
        url = urlparse.urlsplit(page_url(request, 4))
        args = urlparse.parse_qs(url.query)
        eq_(args, {'foo': ['bar', 'ok'], 'baz': ['5'], 'page': ['4']})


class BuglinkifyTests(TestCase):

    def setUp(self):
        self.bugzilla_url_prefix = 'https://bugzilla.mozilla.org/show_bug.cgi?id='

    def test_with_bug_lcase(self):
        """
        buglinkify should linkify a lowercase bug in a string.
        """
        name = 'Test this string with bug 12345'
        eq_(buglinkify(name),
            'Test this string with <a href="%s12345">bug 12345</a>' %
            self.bugzilla_url_prefix)

    def test_with_bug_ucase(self):
        """
        buglinkify should linkify a capitalized bug in a string.
        """
        name = 'Test this string with Bug 12345'
        eq_(buglinkify(name),
            'Test this string with <a href="%s12345">Bug 12345</a>' %
            self.bugzilla_url_prefix)

    def test_without_bug(self):
        """
        buglinkify should leave string intact without a bug.
        """
        name = 'Test this string with boog 12345'
        eq_(buglinkify(name), name)

    def test_with_extra_numbers(self):
        """
        buglinkify should only linkify the bug.
        """
        name = 'Test this 12345 string with Bug 12345 and 12345'
        eq_(buglinkify(name),
            'Test this 12345 string with <a href="%s12345">Bug 12345</a> and 12345' %
            self.bugzilla_url_prefix)
