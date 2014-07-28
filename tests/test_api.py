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
            ({'country_code': 'at'}, 200, {'CUSTOMERS': []}),
            ({'country_code': 'de'}, 200, {'CUSTOMERS': [{'NAME': 'Hans'}]}),
        ],

        '..getnewargs..': [
            ({}, 400, {u'ERRORS': [u'unknown SERVICE: ..getnewargs..',
                              u'unknown SERVICE: ']}),
        ],

        'subscription.get': [
            ({}, 200, {}),
        ],
        'subscription.setusagedata': [
            (
                {
                    'USAGE_DATE': datetime.datetime(2015, 5, 1),
                    'UNIT_PRICE': decimal.Decimal('17.23'),
                    'CURRENCY_CODE': u'EUR',
                },
                200,
                {}
            ),
        ],
    }

    def test_response(self):
        import fastbill
        response = {
            'SUBSCRIPTIONS': [
                {
                    'SUBSCRIPTION': {
                        'SUBSCRIPTION_ID': '1101',
                        'CUSTOMER_ID': '296526',
                        'START': '2013-05-24 13:50:33',
                        'NEXT_EVENT': '2013-06-24 13:50:33',
                        'CANCELLATION_DATE': '2013-06-24 13:50:33',
                        'STATUS': 'canceled',
                        'ARTICLE_NUMBER': '1',
                        'SUBSCRIPTION_EXT_UID': '',
                        'LAST_EVENT': '2013-05-24 13:50:33',
                    }
                }
            ]
        }

        class FakeAPI(object):
            def subscription_get(self, filter=None):
                return fastbill.FastbillResponse(response, self)

        resp = fastbill.FastbillResponse(response, FakeAPI())
        self.assertEquals(response,
                          resp.subscriptions[0].subscription.subscription)
        self.assertRaises(AttributeError, getattr, resp, 'blah')
        resp_iter = iter(resp)
        self.assertEqual(next(resp_iter),
                         response['SUBSCRIPTIONS'][0])
        self.assertRaises(StopIteration, next, resp_iter)

    @httpretty.activate
    def test_wrapper(self):
        import fastbill

        api = fastbill.FastbillWrapper(api_email, api_key)

        for method_name, calls in self.TESTCASES.items():
            method = getattr(api, method_name.replace(".", "_"))

            for (filter_by, http_code, response) in calls:
                def request_callback(method, _, headers):
                    request = json.loads(method.body)
                    request['SERVICE'] = method_name
                    return (http_code, headers, json.dumps({
                        'RESPONSE': response,
                        'REQUEST': request,
                    }, cls=fastbill.CustomJsonEncoder))

                httpretty.register_uri(httpretty.POST,
                                       fastbill.FastbillWrapper.SERVICE_URL,
                                       body=request_callback)
                params = {'filter': filter_by}

                if http_code == 200:
                    result = method(**params)
                    self.assertEqual(result, response)
                else:
                    self.assertRaises(fastbill.FastbillResponseError,
                                      method, **params)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-vv', '--with-doctest'])
