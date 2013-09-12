#!/usr/bin/env python
# encoding: utf-8

import requests
import json

__version__ = '0.1.2'
__author__ = 'Dimitar Roustchev'


class FastbillException(Exception):
    pass


class FastbillResponse(dict):
    ENDPOINTS = ['CUSTOMERS', 'SUBSCRIPTIONS', 'INVOICES', 'TEMPLATES']

    def __iter__(self):
        # If we iterate over the result we just want the values
        # and not the stuff we got sent alongside.
        for ep in self.ENDPOINTS:
            if ep in self.keys():
                return iter(self[ep])
        else:
            return iter([])


class FastbillAPI(object):

    def __init__(self, api_endpoint, email, api_key):
        self.api_endpoint = api_endpoint
        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def __getattr__(self, name):
        endpoint = name.replace("_", ".")

        def func(**kw):
            return self._request(endpoint, **kw)
        return func

    def _request(self, method, **kw):
        payload = {
            'service': method,
        }
        for key in ['limit', 'offset', 'filter', 'data']:
            payload[key] = kw.pop(key, None)

        if kw:
            raise FastbillException("Unknown arguments: %s" %
                                    ", ".join(kw.keys()))

        r = requests.post(self.api_endpoint,
                          auth=self.auth,
                          headers=self.headers,
                          data=json.dumps(payload))

        if r.status_code != 200:
            raise FastbillException(str(r.status_code) + ' ' + str(r.reason))
        else:
            response = r.json.get('RESPONSE')
            if response.get('ERRORS'):
                raise FastbillException('\n'.join(response.get('ERRORS')))
            return FastbillResponse(response)
