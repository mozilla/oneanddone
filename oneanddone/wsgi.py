"""
WSGI config for oneanddone project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oneanddone.settings')

from django.conf import settings  # NOQA
from django.core.cache.backends.memcached import BaseMemcachedCache  # NOQA
from django.core.wsgi import get_wsgi_application  # NOQA

from whitenoise.django import DjangoWhiteNoise  # NOQA

application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# Add media files
if settings.MEDIA_ROOT and settings.MEDIA_URL:
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)

# Fix django closing connection to memcached after every request (#11331)
# From https://devcenter.heroku.com/articles/memcachier#django
BaseMemcachedCache.close = lambda self, **kwargs: None
