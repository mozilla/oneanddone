# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from urlparse import urlparse

from django.forms import CheckboxSelectMultiple, MultiWidget, URLField
from django.forms import ValidationError
from django.forms.widgets import DateInput, Input, RadioSelect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

import requests


class CalendarInput(DateInput):

    def render(self, name, value, attrs={}):
        if 'class' not in attrs:
            attrs['class'] = 'datepicker'
        return super(CalendarInput, self).render(name, value, attrs)


class DateRangeWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (CalendarInput(attrs=attrs), CalendarInput(attrs=attrs))
        super(DateRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]

    def format_output(self, rendered_widgets):
        return '-'.join(rendered_widgets)


class HorizCheckboxSelect(CheckboxSelectMultiple):

    def render(self, *args, **kwargs):
        output = super(HorizCheckboxSelect, self).render(*args, **kwargs)
        return mark_safe(output.replace(u'<ul>', u'')
                               .replace(u'</ul>', u'')
                               .replace(u'<li>', u'')
                               .replace(u'</li>', u''))


class HorizRadioRenderer(RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class HorizRadioSelect(RadioSelect):
    renderer = HorizRadioRenderer


class RangeInput(Input):
    input_type = 'range'

    def render(self, name, value, attrs=None):
        markup = """
            <div class="range-container">
              <div class="range-row">
                {input} &nbsp; <span class="range-label"></span>
              </div>
              <div class="steps">
                <span style="left: 0%">0</span>
                <span style="left: 25%">15</span>
                <span style="left: 50%">30</span>
                <span style="left: 75%">45</span>
                <span style="left: 100%">60</span>
              </div>
            </div>
        """.format(input=super(RangeInput, self).render(name, value, attrs))

        return mark_safe(markup)


class MyURLField(URLField):

    def clean(self, value):
        if not value:
            return None
        url = urlparse(value)
        if url.scheme == '':
            value = 'http://' + value
        try:
            r = requests.get(value, timeout=10, verify=False)
            if not r.ok:
                raise ValidationError(_('The website is not reachable. Please enter a valid url.'))
        except requests.exceptions.RequestException:
            raise ValidationError(_('The website is not reachable. Please enter a valid url.'))
        return super(MyURLField, self).clean(value)
