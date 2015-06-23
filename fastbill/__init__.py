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
import logging

__version__ = '0.5.2'
__author__ = 'python-fastbill contributors'


logger = logging.getLogger("fastbill.api")


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
    pass


class FastbillResponseError(FastbillHttpError):
    """Raised if Fastbill reports errors in the response."""
    pass


CURRENCIES = {
    1: u'EUR',
    2: u'GBP',
    3: u'CHF',
    4: u'USD',
    5: u'ZAR',
    6: u'AUD',
    7: u'CAD',
    8: u'PLN',
    9: u'CZK',
    10: u'CNY',
    11: u'HUF',
    12: u'BRL',
    13: u'RON',
    14: u'CVE',
    15: u'DKK',
    16: u'SEK',
    17: u'INR',
    18: u'RUB',
    20: u'HRK',
    22: u'MXN',
    25: u'NOK',
}


class FastbillResponse(dict):

    """Wrap Fastbill's response and help with iterating over the
    returned result."""

    SECTIONS = ['ARTICLES', 'CUSTOMERS', 'INVOICES', 'ITEMS', 'SUBSCRIPTIONS',
                'TEMPLATES', 'EXPENSES']

    def __init__(self, resp, api):
        self.api = api
        super(FastbillResponse, self).__init__(resp)

    def __reduce__(self):
        return (self.__class__, (dict(self), None), None, None, None)

    @property
    def currency(self):
        return CURRENCIES[int(self.currency_code)]

    def __getattr__(self, key):
        key = key.upper()
        if key not in self and self.api is not None:
            id_value = key + "_ID"
            if id_value in self:
                return getattr(self.api, "%s_get" % key.lower())(
                    filter={id_value: self[id_value]}
                )
            else:
                raise AttributeError("%s not found." % key)
        elif type(self[key]) == dict:
            return self.__class__(self[key], self.api)
        elif type(self[key]) == list:
            return [self.__class__(entry, self.api)
                    for entry in self[key]]
        else:
            return self[key]

    def __iter__(self):
        # If we iterate over the result we just want the values
        # and not the stuff we got sent alongside.
        for section in self.SECTIONS:
            if section in self:
                return iter(self[section])

        return iter([])


def _abort(http_resp, errors=None):
    if errors:
        desc = "Errors were"
        msg = '\n'.join(" > %s" % error for error in errors)
    else:
        desc = "Response was"
        msg = http_resp.content

    raise FastbillResponseError(u"%d %s\n%s:\n%s" % (
        http_resp.status_code, http_resp.reason, desc, msg))


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

    def __init__(self, email, api_key,
                 session=None,
                 service_url=None,
                 name=None):
        if service_url is not None:
            self.SERVICE_URL = service_url

        logger.debug("Using endpoint %r", self.SERVICE_URL)

        if session is None:
            session = requests

        # We use this so clients can identify the API by some arbitrary name.
        # This is useful when dealing with many distinct accounts.
        if name is not None:
            assert isinstance(name, basestring), "Only strings please."
        self.name = name

        self.session = session
        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def __repr__(self):
        return "<%s%s at 0x%x>" % (
            self.__class__.__name__,
            " %s" % self.name if self.name is not None else '',
            id(self)
        )

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError("No such attribute: %s" % name)

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

        data = json.dumps(fb_request,
                          cls=CustomJsonEncoder)
        logger.debug("Sending data: %r", data)

        http_resp = self.session.post(self.SERVICE_URL,
                                      auth=self.auth,
                                      headers=self.headers,
                                      data=data)
        try:
            response = http_resp.json()
        except ValueError:
            logger.debug("Got data: %r", http_resp.content)
            _abort(http_resp)
        else:
            logger.debug("Got data: %r", response)

        errors = response['RESPONSE'].get('ERRORS')
        if errors:
            _abort(http_resp, errors)

        # If Fastbill should ever remove the REQUEST or SERVICE section
        # from their responses, just remove the checks.
        if response['REQUEST']['SERVICE'] != method:
            raise FastbillError(
                "API Error: Got response from wrong service.")

        return FastbillResponse(response['RESPONSE'], self)
