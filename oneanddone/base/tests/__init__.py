# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.test import TestCase as OriginalTestCase


class TestCase(OriginalTestCase):
    """Base class for tests across the site."""
    def shortDescription(self):
        return None
