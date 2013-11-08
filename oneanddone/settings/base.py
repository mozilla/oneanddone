# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from funfactory.settings_base import *


# Django Settings
##############################################################################

# Defines the views served for root URLs.
ROOT_URLCONF = 'oneanddone.urls'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'oneanddone.base',

    # Third-party apps.
    'jingo_minify',
]

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
]

# Accepted locales
PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr',)

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'base': (
            'css/sandstone/sandstone-resp.less',
            'css/one-and-done.less'
        ),
    },
    'js': {
        'base': (
            'js/site.js',
        ),
    }
}

# Use staticfiles loaders for finding resources for minification.
JINGO_MINIFY_USE_STATIC = True

# Do not preprocess LESS files.
LESS_PREPROCESS = False

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


# Project-specific Settings
##############################################################################

