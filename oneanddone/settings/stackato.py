# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

import dj_database_url

from . import base


# Database
##############################################################################

DATABASES = {
    'default': dj_database_url.config()
}

# Uncomment this and set to all slave DBs in use on the site.
# SLAVE_DATABASES = ['slave']


# Environment-specific Settings
##############################################################################

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('MEMCACHE_URL'),
    }
}

# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = os.environ.get('DJANGO_DEBUG', False)
TEMPLATE_DEBUG = os.environ.get('DJANGO_TEMPLATE_DEBUG', False)

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = os.environ.get('DJANGO_DEV', False)

# Should robots.txt allow web crawlers? Set this to True for production
ENGAGE_ROBOTS = True

# Uncomment this line if you are running a local development install without
# HTTPS to disable HTTPS-only cookies.
SESSION_COOKIE_SECURE = False

# django-browserid requires you to specify audiences that are valid for your
# site. An audience is a protocol + hosename + port that users will use to
# access your site.
#
# In development, this is typically 'http://localhost:8000' or similar. In
# production, this is typically the protocol and domain for the site.

BROWSERID_AUDIENCES = os.environ.get('BROWSERID_AUDIENCE', 'https://oneanddone.paas.allizom.org').split(',')

# Time zone for the current installation. Default is America/Chicago. See
# http://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of
# valid timezone values.
TIME_ZONE = os.environ.get('DJANGO_TIME_ZONE', 'America/New_York')

# Path to Less binary.
LESS_BIN = os.environ.get('LESSC_BIN', 'lessc')

# Stackato's proxy hides the fact that we're using SSL, so we need to
# tell Django how to determine if a request is using SSL.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Google Analytics ID
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')


# Error Reporting
##############################################################################

# Recipients of traceback emails and other notifications.
ADMINS = (
    ('One and Done Admin', os.environ.get('DJANGO_ADMIN_EMAIL', '')),
)
MANAGERS = ADMINS


# Security
##############################################################################

# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key. It cannot be blank.
HMAC_KEYS = {
    '2013-11-07': os.environ.get('DJANGO_HMAC_KEY', ''),
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(base.BASE_PASSWORD_HASHERS, HMAC_KEYS)

# Make this unique, and don't share it with anybody. It cannot be blank.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'ssssshhhhhh')


# Logging
##############################################################################

# SYSLOG_TAG = "oneanddone_app"
# LOGGING = dict(loggers=dict(playdoh={'level': logging.DEBUG}))

# Common Event Format logging parameters
# CEF_PRODUCT = 'Playdoh'
# CEF_VENDOR = 'Mozilla'

# Email
##############################################################################

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'root@localhost')
