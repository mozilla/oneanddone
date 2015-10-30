from django.conf import settings
from django.conf.urls import include, url
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


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    # Generate robots.txt
    url(r'^robots\.txt$',
        lambda r: HttpResponse(
            'User-agent: *\n{0}: /'.format('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
            content_type='text/plain')),

    url(r'', include('django_browserid.urls')),

    url(r'', include('oneanddone.base.urls')),
    url(r'', include('oneanddone.users.urls')),
    url(r'', include('oneanddone.tasks.urls')),
]


# In DEBUG mode, serve media files through Django and make error views
# viewable.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^403/$', handler403),
        url(r'^404/$', handler404),
        url(r'^500/$', handler500),
    ]
