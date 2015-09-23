# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

import bleach
import jinja2
from markdown import markdown


class BaseModel(models.Model):
    """
    Base class for models which adds utility methods.
    """

    class Meta:
        abstract = True

    def _yield_html(self, field):
        """
        Return the requested field for a task after parsing them as
        markdown and bleaching/linkifying them.
        """
        html = markdown(field, output_format='html5')
        linkified_html = bleach.linkify(html, parse_email=True)
        cleaned_html = bleach.clean(linkified_html, tags=settings.INSTRUCTIONS_ALLOWED_TAGS,
                                    attributes=settings.INSTRUCTIONS_ALLOWED_ATTRIBUTES)
        return jinja2.Markup(cleaned_html)

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
