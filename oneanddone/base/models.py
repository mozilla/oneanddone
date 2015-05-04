# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    """
    Base class for models which adds utility methods.
    """

    class Meta:
        abstract = True

    @classmethod
    def choice_display_extra_expression(self, field):
        exp = 'CASE %s ' % field
        state_field = self._meta.get_field_by_name(field)[0]
        for choice in state_field.choices:
            exp += "WHEN %s THEN '%s' " % (choice[0], choice[1])
        exp += "END"
        return exp


class CreatedByModel(models.Model):
    """
    Abstract model that records the user that created it.
    """
    creator = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        abstract = True


class CreatedModifiedModel(BaseModel):
    """
    Abstract model that tracks when an instance is created and modified.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
