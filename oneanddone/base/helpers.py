from jingo import register
from jingo_minify.helpers import get_css_urls
from jinja2 import Markup


@register.function
def less_css(bundle):
    """
    Similar to jingo_minify's css helper, but uses rel="stylesheet/less"
    instead of rel="stylesheet".
    """
    urls = get_css_urls(bundle)
    link_tag = '<link rel="stylesheet/less" media="screen,projection,tv" href="{0}" />'
    return Markup('\n'.join([link_tag.format(url) for url in urls]))
