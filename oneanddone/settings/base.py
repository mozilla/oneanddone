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

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        '..'
    ))


def path(*dirs):
    return os.path.join(ROOT, *dirs)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

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
    'django_nose',
    'jingo_minify',
    'product_details',
    'rest_framework',
    'rest_framework.authtoken',
    'tower',
    'session_csrf',
]

for app in config('EXTRA_APPS', default='', cast=Csv()):
    INSTALLED_APPS.append(app)

MIDDLEWARE_CLASSES = (
    'oneanddone.base.middleware.LocaleURLMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'oneanddone.base.middleware.TimezoneMiddleware',
    'oneanddone.base.middleware.ClosedTaskNotificationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'oneanddone.base.context_processors.i18n',
    'oneanddone.base.context_processors.globals',
)

TEMPLATE_DIRS = (
    path('templates'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

# Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key in your local settings.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)
HMAC_KEYS = {  # for bcrypt only
    # '2012-06-06': 'cheesecake',
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

DEV = config('DEV', default=DEBUG, cast=bool)

TEMPLATE_DEBUG = config('DEBUG', default=DEBUG, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

ROOT_URLCONF = 'oneanddone.urls'

WSGI_APPLICATION = 'oneanddone.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': config(
        'DATABASE_URL',
        cast=dj_database_url.parse
    )
}

SLAVE_DATABASES = []

DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = config('USE_I18N', default=True, cast=bool)

USE_L10N = config('USE_L10N', default=True, cast=bool)

USE_TZ = config('USE_TZ', default=True, cast=bool)

# Gettext text domain
TEXT_DOMAIN = 'messages'
STANDALONE_DOMAINS = [TEXT_DOMAIN, 'javascript']
TOWER_KEYWORDS = {'_lazy': None}
TOWER_ADD_HEADERS = True

# Tells the product_details module where to find our local JSON files.
# This ultimately controls how LANGUAGES are constructed.
PROD_DETAILS_DIR = path('lib/product_details_json')

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
    langs = DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs if lang in product_details.languages])

LANGUAGES = lazy(lazy_langs, dict)()

STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))
STATIC_URL = config('STATIC_URL', '/static/')

MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_URL = config('MEDIA_URL', '/media/')

SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)

TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Django-CSP
CSP_DEFAULT_SRC = (
    "'self'",
)
CSP_FONT_SRC = (
    "'self'",
    'http://*.mozilla.net',
    'https://*.mozilla.net'
)
CSP_IMG_SRC = (
    "'self'",
    'http://*.mozilla.net',
    'https://*.mozilla.net',
)
CSP_SCRIPT_SRC = (
    "'self'",
    'http://www.mozilla.org',
    'https://www.mozilla.org',
    'http://*.mozilla.net',
    'https://*.mozilla.net',
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    'http://www.mozilla.org',
    'https://www.mozilla.org',
    'http://*.mozilla.net',
    'https://*.mozilla.net',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SESSION_COOKIE_SECURE = not DEBUG

# Third-party Library Settings
##############################################################################


def JINJA_CONFIG():
    config = {
        'extensions': [
            'tower.template.i18n',
            'jinja2.ext.do',
            'jinja2.ext.with_',
            'jinja2.ext.loopcontrols'
        ],
        'finalize': lambda x: x if x is not None else ''
    }
    return config

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'registration',
    'browserid',
    'memcached',
]

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'base': (
            'browserid/persona-buttons.css',
            'css/sandstone/sandstone-resp.less',
            'css/one-and-done.less',
            'css/slider.css',
            'css/smoothness/jquery-ui-1.10.4.custom.css',
            'css/datatables/jquery.dataTables.css'
        ),
    },
    'js': {
        'base': (
            'js/libs/jquery-2.0.3.min.js',
            'browserid/api.js',
            'browserid/browserid.js',
            'js/site.js',
            'js/slider.js',
            'js/libs/jquery-ui-1.10.4.custom.js',
            'js/libs/jquery.dataTables.js'
        ),
    }
}

# Use staticfiles loaders for finding resources for minification.
JINGO_MINIFY_USE_STATIC = True

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

# Do not preprocess LESS files.
LESS_PREPROCESS = False
LESS_BIN = 'lessc'

# Testing configuration.
NOSE_ARGS = ['--logging-clear-handlers', '--logging-filter=-factory,-south']

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
# Also see http://www.google.com/support/webmasters/bin/answer.py?answer=93710
ENGAGE_ROBOTS = False

# Always generate a CSRF token for anonymous users.
ANON_ALWAYS = True

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('oneanddone/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('oneanddone/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],
}


# Authentication settings.
BROWSERID_VERIFY_CLASS = 'oneanddone.users.views.Verify'
LOGIN_URL = reverse_lazy('users.login')
LOGIN_REDIRECT_URL = reverse_lazy('base.home')
LOGIN_REDIRECT_URL_FAILURE = reverse_lazy('users.login')
LOGOUT_REDIRECT_URL = reverse_lazy('base.home')

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
    from tower import ugettext_lazy as _lazy

    site_logo = open(finders.find('img/qa-logo.png'), 'rb').read().encode('base64')
    logo_uri = urllib.quote('data:image/png;base64,{image}'.format(image=site_logo), safe=',:;/')
    return {
        'privacyPolicy': 'https://www.mozilla.org/privacy/websites/',
        'siteName': _lazy('One and Done'),
        'termsOfService': 'https://www.mozilla.org/about/legal.html',
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
GOOGLE_ANALYTICS_ID = ''
