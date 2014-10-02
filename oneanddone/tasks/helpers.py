# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import re

from jingo import register
from jinja2 import Markup


@register.filter
def buglinkify(obj):
    return Markup(
        re.sub(
            r'([Bb]ug (\d+))',
            r'<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=\2">\1</a>',
            unicode(obj))
    )


@register.function
def page_url(request, page):
    query = request.GET.copy()
    query['page'] = page
    return ''.join(['?', query.urlencode()])
