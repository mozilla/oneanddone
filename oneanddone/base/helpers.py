# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings

from jingo import register
from jingo_minify.helpers import css, get_css_urls
from jinja2 import Markup


@register.function
def less_css(bundle):
    """
    Similar to jingo_minify's css helper, but uses rel="stylesheet/less"
    instead of rel="stylesheet" when TEMPLATE_DEBUG is True. If
    TEMPLATE_DEBUG is False, this passes the call on to the css helper.
    """
    if not settings.TEMPLATE_DEBUG:
        return css(bundle)

    urls = get_css_urls(bundle)
    link_tag = '<link rel="stylesheet/less" media="screen,projection,tv" href="{0}" />'
    return Markup('\n'.join([link_tag.format(url) for url in urls]))
