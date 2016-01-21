"""
Django settings for oneanddone project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import socket
import urllib

from django.core.urlresolvers import reverse_lazy
from django.utils.functional import lazy
from django.utils.safestring import mark_safe

import dj_database_url
from decouple import Csv, config


_dirname = os.path.dirname
ROOT = _dirname(_dirname(_dirname(os.path.abspath(__file__))))


def path(*args):
    return os.path.join(ROOT, *args)


# Environment-dependent settings. These are loaded from environment
# variables.

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

DEV = config('DEV', default=DEBUG, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

HMAC_KEYS = {
    '2015-04-30': config('DJANGO_HMAC_KEY'),
}

SECRET_KEY = config('DJANGO_SECRET_KEY')

DATABASES = {
    'default': config(
        'DATABASE_URL',
        cast=dj_database_url.parse
    )
}

ROOT_URLCONF = 'oneanddone.urls'

WSGI_APPLICATION = 'oneanddone.wsgi.application'

# Django Settings
##############################################################################

INSTALLED_APPS = [
    'oneanddone.base',
    'oneanddone.tasks',
    'oneanddone.users',

    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Third-party apps.
    'commonware.response.cookies',
    'django_ace',
    'django_browserid',
    'django_jinja',
    'django_jinja.contrib._humanize',  # Adds django humanize filters
    'django_nose',
    'pipeline',
    'rest_framework',
    'rest_framework.authtoken',
    'session_csrf',
]

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oneanddone.base.middleware.TimezoneMiddleware',
    'oneanddone.base.middleware.ClosedTaskNotificationMiddleware',
)

CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'oneanddone.base.context_processors.i18n',
    'oneanddone.base.context_processors.globals',
)

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            # Use jinja2/ for jinja templates
            'app_dirname': 'jinja2',
            # Don't figure out which template loader to use based on
            # file extension
            'match_extension': '',
            'newstyle_gettext': True,
            'context_processors': CONTEXT_PROCESSORS,
            'undefined': 'jinja2.Undefined',
            'extensions': [
                'django_jinja.builtins.extensions.CacheExtension',
                'django_jinja.builtins.extensions.CsrfExtension',
                'django_jinja.builtins.extensions.DjangoFiltersExtension',
                'django_jinja.builtins.extensions.StaticFilesExtension',
                'django_jinja.builtins.extensions.TimezoneExtension',
                'django_jinja.builtins.extensions.UrlsExtension',
                'jinja2.ext.autoescape',
                'jinja2.ext.do',
                'jinja2.ext.i18n',
                'jinja2.ext.loopcontrols',
                'jinja2.ext.with_',
                'pipeline.templatetags.ext.PipelineExtension',
            ],
            'globals': {
                'browserid_info': 'django_browserid.helpers.browserid_info',
                'browserid_login': 'django_browserid.helpers.browserid_login',
                'browserid_logout': 'django_browserid.helpers.browserid_logout'
            }
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': CONTEXT_PROCESSORS
        }
    },
]

AUTHENTICATION_BACKENDS = [
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True


# Email

SERVER_EMAIL = config('OUTBOUND_EMAIL_ADDRESS', default='root@localhost')

# Postmark Email addon
POSTMARK_API_KEY = config('POSTMARK_API_TOKEN', default='')
POSTMARK_SENDER = SERVER_EMAIL
POSTMARK_TEST_MODE = False
POSTMARK_TRACK_OPENS = False

# Log emails to console if the Postmark credentials are missing.
if POSTMARK_API_KEY:
    EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache config
# If the environment contains configuration data for Memcached, use
# PyLibMC for the cache backend. Otherwise, default to an in-memory
# cache.
if os.environ.get('MEMCACHEDCLOUD_SERVERS') is not None:
    CACHES = {
        'default': {
            'BACKEND': 'django_bmemcached.memcached.BMemcached',
            'LOCATION': os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
            'OPTIONS': {
                'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'),
                'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD')}
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 60,
        },
    }


# Internationalization

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('DJANGO_TIME_ZONE', default='America/New_York')

USE_I18N = config('USE_I18N', default=True, cast=bool)

USE_L10N = config('USE_L10N', default=True, cast=bool)

USE_TZ = config('USE_TZ', default=True, cast=bool)

# Accepted locales
PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr',)

DEV_LANGUAGES = PROD_LANGUAGES


def lazy_lang_url_map():
    from django.conf import settings
    langs = settings.DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()


# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = sorted(DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES)
    return [(lang.lower(), product_details.languages[lang]['native'])
            for lang in langs if lang in product_details.languages]

LANGUAGES = lazy(lazy_langs, list)()


STATIC_ROOT = config('STATIC_ROOT', default=path('static'))
STATIC_URL = config('STATIC_URL', default='/static/')

MEDIA_ROOT = config('MEDIA_ROOT', default=path('media'))
MEDIA_URL = config('MEDIA_URL', default='/media/')

STATICFILES_STORAGE = 'oneanddone.base.storage.GzipManifestPipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)

# Django Pipeline
PIPELINE_CSS = {
    'base': {
        'source_filenames': (
            'browserid/persona-buttons.css',
            'css/sandstone/sandstone-resp.less',
            'css/one-and-done.less',
            'css/slider.css',
            'css/smoothness/jquery-ui-1.10.4.custom.css',
            'css/datatables/jquery.dataTables.css'
        ),
        'output_filename': 'css/base.min.css'
    }
}

PIPELINE_JS = {
    'base': {
        'source_filenames': (
            'js/libs/jquery-2.0.3.min.js',
            'browserid/api.js',
            'browserid/browserid.js',
            'js/site.js',
            'js/slider.js',
            'js/libs/jquery-ui-1.10.4.custom.js',
            'js/libs/jquery.dataTables.js'
        ),
        'output_filename': 'js/base.min.js'
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)

PIPELINE_DISABLE_WRAPPER = True

PIPELINE_YUGLIFY_BINARY = path('node_modules/.bin/yuglify')

PIPELINE_LESS_BINARY = path('node_modules/.bin/lessc')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_browserid': {
            'handlers': ['console'],
        },
    }
}

# Third-party Library Settings
##############################################################################

# Testing configuration.
NOSE_ARGS = ['--logging-clear-handlers', '--logging-filter=-factory,-django.db']

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
# Also see http://www.google.com/support/webmasters/bin/answer.py?answer=93710
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Error Reporting
##############################################################################

# Recipients of traceback emails and other notifications.
ADMINS = (
    ('One and Done Admin', config('DJANGO_ADMIN_EMAIL', default='')),
)
MANAGERS = ADMINS


# Authentication settings.
BROWSERID_VERIFY_CLASS = 'oneanddone.users.views.Verify'
LOGIN_URL = reverse_lazy('users.login')
LOGIN_REDIRECT_URL = reverse_lazy('base.home')
LOGIN_REDIRECT_URL_FAILURE = reverse_lazy('users.login')
LOGOUT_REDIRECT_URL = reverse_lazy('base.home')

BROWSERID_AUDIENCES = config('BROWSERID_AUDIENCE',
                             default='http://localhost:8000, '
                             'http://127.0.0.1:8000, http://localhost:8081',
                             cast=Csv())

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'static', 'admin', 'api', 'browserid']

# Celery

# True says to simulate background tasks without actually using celeryd.
# Good for local development in case celeryd is not running.
CELERY_ALWAYS_EAGER = True

BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Time in seconds before celery.exceptions.SoftTimeLimitExceeded is raised.
# The task can catch that and recover but should exit ASAP.
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 10


# Permissions for the REST api
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except socket.error:
    DOMAIN = 'localhost'
PROTOCOL = "http://"
PORT = 80


# Lazy-load request args since they depend on certain settings.
def _request_args():
    from django.contrib.staticfiles import finders
    from django.utils.translation import ugettext_lazy as _lazy

    site_logo = open(finders.find('img/qa-logo.png'), 'rb').read().encode('base64')
    logo_uri = urllib.quote('data:image/png;base64,{image}'.format(image=site_logo), safe=',:;/')
    return {
        'privacyPolicy': 'https://www.mozilla.org/privacy/websites/',
        'siteName': _lazy(u'One and Done'),
        'termsOfService': 'https://www.mozilla.org/about/legal/',
        'siteLogo': mark_safe(logo_uri),
        'backgroundColor': '#E0DDD4',
    }
BROWSERID_REQUEST_ARGS = lazy(_request_args, dict)()

# Project-specific Settings
##############################################################################
# Number of days that a one-time task attempt can be open before it expires
TASK_ATTEMPT_EXPIRATION_DURATION = 30

# The minimum duration for a complete task attempt, in seconds, to
# be considered valid
MIN_DURATION_FOR_COMPLETED_ATTEMPTS = 120

# Whitelisted tags allowed to be used in task instructions.
INSTRUCTIONS_ALLOWED_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'dl',
    'dt',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'i',
    'img',
    'li',
    'ol',
    'p',
    'strong',
    'ul',
]

# Whitelisted attributes allowed to be used in task instruction tags.
INSTRUCTIONS_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
    'img': ['src', 'alt', 'title'],
}

# Google Analytics ID
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
