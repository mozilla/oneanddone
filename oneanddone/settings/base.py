# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import urllib

from django.core.urlresolvers import reverse_lazy
from django.utils.safestring import mark_safe

from funfactory.settings_base import *
from tower import ugettext_lazy as _lazy


# Django Settings
##############################################################################

# Defines the views served for root URLs.
ROOT_URLCONF = 'oneanddone.urls'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

# Support timezone-aware datetimes.
USE_TZ = True

INSTALLED_APPS = (
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
    'funfactory',
    'jingo_minify',
    'mptt',
    'product_details',
    'rest_framework',
    'rest_framework.authtoken',
    'south',
    'tower',
    'session_csrf',
)

MIDDLEWARE_CLASSES = (
    'funfactory.middleware.LocaleURLMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'oneanddone.base.middleware.TimezoneMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'funfactory.context_processors.i18n',
    'funfactory.context_processors.globals',
    'django_browserid.context_processors.browserid',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

LOCALE_PATHS = (
    os.path.join(ROOT, 'locale'),
)


# Third-party Libary Settings
##############################################################################

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'registration',
    'browserid',
]

# Accepted locales
PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr',)

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'base': (
            'browserid/persona-buttons.css',
            'css/sandstone/sandstone-resp.less',
            'css/one-and-done.less',
            'css/slider.css',
        ),
    },
    'js': {
        'base': (
            'js/libs/jquery-2.0.3.min.js',
            'browserid/browserid.js',
            'js/site.js',
            'js/slider.js',
        ),
    }
}

# Use staticfiles loaders for finding resources for minification.
JINGO_MINIFY_USE_STATIC = True

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
DOMAIN_METHODS['messages'] = [
    ('oneanddone/**.py',
        'tower.management.commands.extract.extract_tower_python'),
    ('oneanddone/**/templates/**.html',
        'tower.management.commands.extract.extract_tower_template'),
    ('templates/**.html',
        'tower.management.commands.extract.extract_tower_template'),
]

# Authentication settings.
BROWSERID_VERIFY_CLASS = 'oneanddone.users.views.Verify'
LOGIN_URL = reverse_lazy('users.login')
LOGIN_REDIRECT_URL = reverse_lazy('base.home')
LOGIN_REDIRECT_URL_FAILURE = reverse_lazy('users.login')
LOGOUT_REDIRECT_URL = reverse_lazy('base.home')

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES.append('api')

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


# Lazy-load request args since they depend on certain settings.
def _request_args():
    from django.contrib.staticfiles import finders

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
