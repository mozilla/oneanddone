import datetime
import json
import re
import urllib
import urlparse

from django.contrib.humanize.templatetags import humanize
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils import six
from django.utils.encoding import smart_str
try:
    from django.utils.encoding import smart_unicode as smart_text
except ImportError:
    from django.utils.encoding import smart_text

import jinja2
from django_jinja import library


@library.filter
def fe(s, *args, **kwargs):
    """Format a safe string with potentially unsafe arguments, then return a
    safe string."""
    s = six.text_type(s)
    args = [jinja2.escape(smart_text(v)) for v in args]
    for k in kwargs:
        kwargs[k] = jinja2.escape(smart_text(kwargs[k]))
    return jinja2.Markup(s.format(*args, **kwargs))


@library.filter
def buglinkify(obj):
    return jinja2.Markup(
        re.sub(
            r'([Bb]ug (\d+))',
            r'<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=\2">\1</a>',
            unicode(obj))
    )


@library.global_function
def page_url(request, page):
    query = request.GET.copy()
    query['page'] = page
    return ''.join(['?', query.urlencode()])


@library.global_function
def thisyear():
    """The current year."""
    return jinja2.Markup(datetime.date.today().year)


@library.global_function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@library.filter
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


@library.filter
def urlencode(txt):
    """Url encode a path."""
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return urllib.quote_plus(txt)


@library.global_function
def static(path):
    return staticfiles_storage.url(path)


@library.filter
def to_json(value):
    return json.dumps(value)


@library.filter
def naturalday(source, arg=None):
    return humanize.naturalday(source, arg)


@library.filter
def naturaltime(source):
    return humanize.naturaltime(source)
