# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests


class BugzillaUtils(object):

    def __init__(self):
        self.baseurl = 'https://bugzilla.mozilla.org/rest/bug'

    def _request_json(self, url, params):
        """ Returns the json-encoded response from Bugzilla@Mozilla, if any """
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        if not r.ok:
            r.raise_for_status()
        elif data.get('error'):
            # According to
            # http://www.bugzilla.org/docs/tip/en/html/api/Bugzilla/WebService/Server/REST.html#ERRORS
            errno = data.get('code')
            message = ''.join([data.get('message'), ' (Error ', str(errno), ')'])
            if errno >= 0 and errno <= 100000:
                # Transient error (e.g. bad query)
                raise ValueError(message)
            if errno < 0 or errno > 100000:
                # Fatal error in Bugzilla, or error thrown by the JSON-RPC
                # library that Bugzilla uses
                raise RuntimeError(message)
        return data

    def request_bug(self, bug_id, fields=None):
        """ Returns bug with id `bug_id` from Buzgilla@Mozilla, if any """
        params = {}
        if fields:
            params['include_fields'] = ','.join(fields)
        url = ''.join([self.baseurl, '/', str(bug_id)])
        bugs = self._request_json(url, params).get('bugs')
        if bugs:
            return bugs[0]
        else:
            return None

    def request_bugcount(self, request_params):
        params = dict(request_params)
        params.update({'count_only': 1})
        response = self._request_json(self.baseurl, params)
        bug_count = response.get('bug_count', '0')
        return int(bug_count)

    def request_bugs(self, request_params, fields=['id', 'summary'],
                     offset=0, limit=99):
        """ Returns list of at most first `limit` bugs (starting at `offset`) from
            Bugzilla@Mozilla, if any. The bugs are ordered by bug id.
        """
        params = dict(request_params)
        params.update({'include_fields': ','.join(fields),
                      'offset': offset, 'limit': limit})
        return self._request_json(self.baseurl, params).get('bugs', [])
