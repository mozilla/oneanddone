# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.forms.widgets import Input
from django.utils.safestring import mark_safe


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
