from django.conf import settings
from django.conf.urls import patterns, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.shortcuts import render


# Auto-discover admin interface definitions.
admin.autodiscover()


def handler500(request):
    return render(request, '500.html', status=500)


def handler403(request):
    return render(request, '403.html', status=403)


def handler404(request):
    return render(request, '404.html', status=404)


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),

    # Generate robots.txt
    (r'^robots\.txt$',
        lambda r: HttpResponse(
            'User-agent: *\n{0}: /'.format('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
            content_type='text/plain')),

    (r'', include('django_browserid.urls')),

    (r'', include('oneanddone.base.urls')),
    (r'', include('oneanddone.users.urls')),
    (r'', include('oneanddone.tasks.urls'))

)


# In DEBUG mode, serve media files through Django and make error views
# viewable.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns(
        '',
        (r'^403/$', handler403),
        (r'^404/$', handler404),
        (r'^500/$', handler500),
    )
