import datetime
import urllib
import urlparse

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.template import defaultfilters
from django.utils.encoding import smart_str
from django.utils.html import strip_tags

from jingo import register
from jingo_minify.helpers import css, get_css_urls
import jinja2
from jinja2 import Markup

from oneanddone.base.urlresolvers import reverse

static = register.function(static)


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


# Brought over from funfactory

# Yanking filters from Django.
register.filter(strip_tags)
register.filter(defaultfilters.timesince)
register.filter(defaultfilters.truncatewords)


@register.function
def thisyear():
    """The current year."""
    return jinja2.Markup(datetime.date.today().year)


@register.function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@register.filter
def urlparams(url_, hash=None, **query):
    """Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = _urlencode([(k, v) for k, v in query_dict.items()
                               if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()


def _urlencode(items):
    """A Unicode-safe URLencoder."""
    try:
        return urllib.urlencode(items)
    except UnicodeEncodeError:
        return urllib.urlencode([(k, smart_str(v)) for k, v in items])


@register.filter
def urlencode(txt):
    """Url encode a path."""
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return urllib.quote_plus(txt)
