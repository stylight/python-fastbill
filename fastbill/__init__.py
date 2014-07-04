#!/usr/bin/env python
# encoding: utf-8

"""
FastbillWrapper
~~~~~~~~~~~~~~~

This library provides a very thin wrapper around Fastbill's HTTP API.

What it does do:

 * Encapsulate the HTTP request generation and response de-jsoning.

What it specifically doesn't do:

 * Check the data you send to Fastbill for consistency.
 * Verify the data coming back is what you expect.
 * Convert types. (Especially not dates or times)

:copyright: (c) 2013,2014 Stylight GmbH
:licence: MIT, see LICENSE for more details.

"""

# Pylint can't infer some attributes of request's response object.
# pylint: disable-msg=E1103

import decimal
decimal_types = (decimal.Decimal,)

try:
    import cdecimal
    decimal_types += (cdecimal.Decimal,)
    decimal = cdecimal
except ImportError:
    pass

import datetime
import json
import requests
import warnings

__version__ = '0.2.1'
__author__ = 'Dimitar Roustchev'


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal_types):
            return str(o)
        elif type(o) == datetime.date:
            return o.strftime('%Y-%m-%d')
        elif type(o) == datetime.datetime:
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super(CustomJsonEncoder, self).default(o)


class FastbillError(Exception):
    """Baseclass for all API errors."""
    pass


class FastbillRequestError(FastbillError):
    """Raised if there are problems with the request."""
    pass


class FastbillHttpError(FastbillError):
    """Raised if there are problems with the API server."""
    pass


class FastbillResponseError(FastbillError):
    """Raised if Fastbill reports errors in the response."""
    pass


class FastbillResponse(dict):

    """Wrap Fastbill's response and help with iterating over the
    returned result."""

    SECTIONS = ['CUSTOMERS', 'SUBSCRIPTIONS', 'INVOICES', 'TEMPLATES', 'ITEMS']

    def __iter__(self):
        # If we iterate over the result we just want the values
        # and not the stuff we got sent alongside.
        for section in self.SECTIONS:
            if section in self.keys():
                return iter(self[section])

        return iter([])


class FastbillWrapper(object):

    u"""Wrap Fastbill's HTTP API for easier usage.

    This object doesn't implement any of the concrete API methods, but
    rather implements the common pattern of all these methods.

    The effect is that you can call any Fastbill "services" that are
    available and (given no error on Fastbill's side) it should work.

    You will always be handed the RESPONSE section of the returned data.
    In case of errors a `FastbillException` will be raised.

    """

    SERVICE_URL = "https://automatic.fastbill.com/api/1.0/api.php"

    def __init__(self, email, api_key, service_url=None):
        if service_url is not None:
            self.SERVICE_URL = service_url

        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def __getattr__(self, name):
        method = name.replace("_", ".")

        def api_method(**kw):
            """Autogenerated method which calls `_request` with the
            correct parameter.

            The service-name will be deduced from the method-name.
            """
            return self._request(method, **kw)
        return api_method

    def _request(self, method, **kw):
        """Do the actual request to Fastbill's API server.

        If sucessful returns the RESPONSE section the of response, in
        case of an error raises a subclass of FastbillError.
        """
        fb_request = {
            'service': method,
        }
        for key in ['limit', 'offset', 'filter', 'data']:
            fb_request[key] = kw.pop(key, None)

        if kw:
            raise FastbillRequestError("Unknown arguments: %s" %
                                       ", ".join(kw.keys()))

        http_resp = requests.post(self.SERVICE_URL,
                                  auth=self.auth,
                                  headers=self.headers,
                                  data=json.dumps(fb_request,
                                                  cls=CustomJsonEncoder))

        if http_resp.status_code != 200:
            raise FastbillHttpError(str(http_resp.status_code) + ' ' +
                                    str(http_resp.reason))
        else:
            # Support both old and new requests semantics for now.
            if callable(http_resp.json):
                response = http_resp.json()
            else:
                warnings.warn("Your requests module is too old. "
                              "Consider upgrading.",
                              DeprecationWarning)
                response = http_resp.json

            # The next two checks are here as a failsafe to prevent against
            # (imaginable) multi-threading problems of the API.
            # Disclaimer: I haven't seen those and don't suspect them to
            # appear, but I can imagine them and this field is perfectly
            # usable to prevent these responses from slipping through.

            # If Fastbill should ever remove the REQUEST or SERVICE section
            # from their responses, just remove the checks.
            if response['REQUEST']['SERVICE'] != method:
                raise FastbillError(
                    "API Error: Got response from wrong service.")

            #if response['REQUEST'] != fb_request:
                #raise FastbillError(
                    #"API Error: Got response to wrong request.")

            errors = response['RESPONSE'].get('ERRORS')
            if errors:
                raise FastbillResponseError('\n'.join(errors))
            return FastbillResponse(response['RESPONSE'])
