"""
WSGI config for oneanddone project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oneanddone.settings')

from django.conf import settings
from django.core.wsgi import get_wsgi_application

import newrelic.agent
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# Add media files
if settings.MEDIA_ROOT and settings.MEDIA_URL:
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)

# Add NewRelic
NEW_RELIC_LICENSE_KEY = os.environ.get('NEW_RELIC_LICENSE_KEY', False)
NEW_RELIC_APP_NAME = os.environ.get('NEW_RELIC_APP_NAME', False)
if NEW_RELIC_LICENSE_KEY and NEW_RELIC_APP_NAME:
    newrelic.agent.initialize()
    application = newrelic.agent.wsgi_application()(application)
