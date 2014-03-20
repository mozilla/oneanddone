# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from mock import Mock
from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.admin import RecordCreatorMixin


class FakeModelAdmin(object):
    def save_model(self, request, obj, form, change):
        return 'saved'


class FakeModelAdminWithMixin(RecordCreatorMixin, FakeModelAdmin):
    pass


class RecordCreatorMixinTests(TestCase):
    def setUp(self):
        self.model_admin = FakeModelAdminWithMixin()

    def test_save_model_no_pk(self):
        """
        If an object isn't saved yet (has no pk), set the creator to the
        request's current user.
        """
        obj = Mock(pk=None)
        request = Mock(user='foo')

        self.model_admin.save_model(request, obj, None, False)
        eq_(obj.creator, request.user)

    def test_save_model_with_pk(self):
        """
        If an object exists in the DB (has a pk), do not change the
        creator.
        """
        obj = Mock(pk=5, creator='bar')
        request = Mock(user='foo')

        self.model_admin.save_model(request, obj, None, False)
        eq_(obj.creator, 'bar')
