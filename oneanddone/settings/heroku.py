# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

# Allow all host headers
ALLOWED_HOSTS = ['*']

if 'HEROKU_APP_NAME' in os.environ:
    BROWSERID_AUDIENCES = ['https://%s.herokuapp.com' % os.getenv('HEROKU_APP_NAME')]
