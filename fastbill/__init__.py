#!/usr/bin/env python
# encoding: utf-8

import requests
import json

__version__ = '0.1'
__author__ = 'Dimitar Roustchev'


def _enum(**enums):
    return type('Enum', (), enums)

CustomerType = _enum(BUSINESS='business', CONSUMER='consumer')
CountryCode = _enum(DE='de', AT='at', CH='ch')
Salutation = _enum(MR='mr', MRS='mrs', FAM='familiy', EMPTY='')
CurrencyCode = _enum(EUR='EUR', CHF='CHF', GBP='GBP', USD='USD')
PaymentType = _enum(TRANSFER=1,
                    DEBIT=2,
                    CASH=3,
                    PAYPAL=4,
                    PREPAYMENT=5,
                    CREDITCARD=6)
PaymentNotice = _enum(YES=1, NO=0)


class FastbillException(Exception):
    pass


class InsufficientParams(FastbillException):
    pass


class FastbillAPI(object):
    API_ENDPOINT = "https://automatic.fastbill.com/api/1.0/api.php"

    ENDPOINTS = ['CUSTOMERS', 'SUBSCRIPTIONS', 'INVOICES', 'TEMPLATES']

    def __init__(self, email, api_key):
        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def __getattr__(self, name):
        endpoint = '.'.join(name.split("_"))

        def func(**kw):
            if hasattr(self, '_' + endpoint):
                pass
            result = self._request(endpoint, **kw)
            # post check
            for ep in self.ENDPOINTS:
                if ep in result:
                    return result[ep]
            return result
        return func

    def _request(self, method, **kw):
        payload = {'service': method,
                   'limit': kw.get('limit'),
                   'offset': kw.get('offset'),
                   'filter': kw.get('filter'),
                   'data': kw.get('data'),
                   }

        r = requests.post(self.API_ENDPOINT,
                          auth=self.auth,
                          headers=self.headers,
                          data=json.dumps(payload))

        if r.status_code != 200:
            raise FastbillException(str(r.status_code) + ' ' + str(r.reason))
        else:
            response = r.json().get('RESPONSE')
            if response.get('ERRORS'):
                raise FastbillException(response.get('ERRORS')[0])
            return r.json().get('RESPONSE')
