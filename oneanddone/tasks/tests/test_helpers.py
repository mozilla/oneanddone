# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import urlparse

from mock import Mock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.helpers import page_url


class PageUrlTests(TestCase):
    def test_basic(self):
        """
        page_url should return a relative link to the current page,
        preserving the GET arguments from the given request, and adding
        a page parameter for the given page.
        """
        request = Mock(GET={'foo': 'bar', 'baz': 5})
        url = urlparse.urlsplit(page_url(request, 4))
        args = urlparse.parse_qs(url.query)
        eq_(args, {'foo': ['bar'], 'baz': ['5'], 'page': ['4']})

    def test_existing_page_arg(self):
        """
        If the current page already has a page GET argument, override
        it.
        """
        request = Mock(GET={'foo': 'bar', 'page': 5})
        url = urlparse.urlsplit(page_url(request, 4))
        args = urlparse.parse_qs(url.query)
        eq_(args, {'foo': ['bar'], 'page': ['4']})
