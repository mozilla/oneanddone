from django.http import Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.cache import never_cache

from django_memcached.util import get_memcached_stats
from django.contrib.auth.decorators import user_passes_test

def get_cache_server_list():
    """Returns configured memcached servers.

    Works with both old-style (CACHE_BACKEND) and new-style (CACHES)
    cache configurations.

    """
    engine = ''

    # Django >= 1.3
    #
    # If somebody uses CACHE_BACKEND instead of CACHES in 1.3, it
    # automatically converts their CACHE_BACKEND configuration to the
    # appropriate CACHES configuration.  So we can safely use
    # parse_backend_conf here and it'll work with both old and new styles.
    try:
        from django.core.cache import parse_backend_conf, DEFAULT_CACHE_ALIAS
        engine, hosts, params = parse_backend_conf(DEFAULT_CACHE_ALIAS)

    # Django < 1.3
    #
    # No parse_backend_conf and DEFAULT_CACHE_ALIAS.
    except ImportError:
        from django.core.cache import parse_backend_uri
        engine, hosts, params = parse_backend_uri(settings.CACHE_BACKEND)

    if 'memcached' not in engine:
        raise ImproperlyConfigured("django-memcached2 only works with memcached.  Currently using '%s'" % engine)

    return hosts if isinstance(hosts, list) else hosts.split(';')

@never_cache
def server_list(request):
    servers = get_cache_server_list()
    statuses = []
    for idx, server in enumerate(servers):
        statuses.append((idx, server, get_memcached_stats(server)))

    context = {
        'statuses': statuses,
    }
    return render_to_response(
        'memcached/server_list.html',
        context,
        context_instance=RequestContext(request)
    )

@never_cache
def server_status(request, index):
    servers = get_cache_server_list()
    try:
        index = int(index)
    except ValueError:
        raise Http404
    try:
        server = servers[index]
    except IndexError:
        raise Http404
    stats = get_memcached_stats(server)
    if not stats:
        raise Http404
    context = {
        'server': server,
        'stats': stats.items(),
    }
    return render_to_response(
        'memcached/server_status.html',
        context,
        context_instance=RequestContext(request)
    )

if getattr(settings, 'DJANGO_MEMCACHED_REQUIRE_STAFF', False):
    server_list = user_passes_test(lambda u: u.is_staff)(server_list)
    server_status = user_passes_test(lambda u: u.is_staff)(server_status)
