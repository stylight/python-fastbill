#!/usr/bin/env python
# encoding: utf-8


api_email = "fastbill@example.com"
api_key = "4"


import datetime
import decimal
import httpretty
import json
import unittest


class JsonTest(unittest.TestCase):

    def test_json_encoder(self):
        import fastbill
        json_dump = json.dumps({
            'date': datetime.date(2016, 6, 2),
            'datetime': datetime.datetime(2015, 5, 1, 14, 42, 17),
            'money': decimal.Decimal("17.23"),
        }, cls=fastbill.CustomJsonEncoder)

        self.assertEqual(
            json_dump,
            '{"date": "2016-06-02", '
            '"money": "17.23", '
            '"datetime": "2015-05-01 14:42:17"}'
        )


class TestWrapper(unittest.TestCase):
    TESTCASES = {
        'customer.get': [
            ({'country_code': 'at'}, {'CUSTOMERS': []}),
            ({'country_code': 'de'}, {'CUSTOMERS': [{'NAME': 'Hans'}]}),
        ],

        'subscription.get': [
            ({}, {}),
        ],
        'subscription.setusagedata': [
            (
                {
                    'USAGE_DATE': datetime.datetime(2015, 5, 1),
                    'UNIT_PRICE': decimal.Decimal('17.23'),
                    'CURRENCY_CODE': u'EUR',
                },
                {}
            ),
        ],
    }

    @httpretty.activate
    def test_wrapper(self):
        import fastbill

        api = fastbill.FastbillWrapper(api_email, api_key)

        for method_name, calls in self.TESTCASES.items():
            method = getattr(api, method_name.replace(".", "_"))

            for (filter_by, response) in calls:
                def request_callback(method, uri, headers):
                    request = json.loads(method.body)
                    request['SERVICE'] = method_name
                    return (200, headers, json.dumps({
                        'RESPONSE': response,
                        'REQUEST': request,
                    }, cls=fastbill.CustomJsonEncoder))

                httpretty.register_uri(httpretty.POST,
                                       fastbill.FastbillWrapper.SERVICE_URL,
                                       body=request_callback)
                result = method(filter=filter_by)
                self.assertEqual(result, response)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-vv', '--with-doctest'])
