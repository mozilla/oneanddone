# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse

from funfactory.monkeypatches import patch


# Activate funfactory monkeypatches.
patch()


urlpatterns = patterns('',
    (r'', include('oneanddone.base.urls')),

    (r'^browserid/', include('django_browserid.urls')),

    # Generate robots.txt
    (r'^robots\.txt$',
        lambda r: HttpResponse(
            'User-agent: *\n{0}: /'.format('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
            mimetype='text/plain'
        )
    )
)


# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
