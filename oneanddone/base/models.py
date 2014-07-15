# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib.auth.models import User
from django.db import models

import caching.base


class CachedModel(caching.base.CachingMixin, models.Model):
    """
    Base class for models which adds caching via django-cache-machine.
    """

    objects = caching.base.CachingManager()

    class Meta:
        abstract = True


class CreatedModifiedModel(models.Model):
    """
    Abstract model that tracts when an instance is created and modified.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatedByModel(models.Model):
    """
    Abstract model that records the user that created it.
    """
    creator = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        abstract = True
