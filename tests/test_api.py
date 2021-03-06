#!/usr/bin/env python
# encoding: utf-8


import datetime
import decimal
import httpretty
import json
import unittest

# Set the endpoint to http because some library combination
# leads to a SSLError when running the test with httpretty.
api_endpoint = "http://automatic.fastbill.com/api/1.0/api.php"
api_email = "fastbill@example.com"
api_key = "4"


RESPONSE_DATA = {
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


class JsonTest(unittest.TestCase):

    def test_json_encoder(self):
        import fastbill
        json_dump = json.dumps({
            'date': datetime.date(2016, 6, 2),
            'datetime': datetime.datetime(2015, 5, 1, 14, 42, 17),
            'money': decimal.Decimal("17.23"),
        }, cls=fastbill.jsonencoder.CustomJsonEncoder)

        self.assertEqual(
            json.loads(json_dump),
            {'date': '2016-06-02',
             'money': '17.23',
             'datetime': '2015-05-01 14:42:17'}
        )


class TestWrapper(unittest.TestCase):
    TESTCASES = {
        'customer.get': [
            ({'country_code': 'at'}, 200, {'CUSTOMERS': []}),
            ({'country_code': 'de'}, 200, {'CUSTOMERS': [{'NAME': 'Hans'}]}),
        ],

        'getnewargs': [
            ({}, 400, {u'ERRORS': [u'unknown SERVICE: getnewargs',
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
        response = RESPONSE_DATA

        class FakeAPI(object):
            def subscription_get(self, filter=None):
                return fastbill.response.FastbillResponse(response, self)

        resp = fastbill.response.FastbillResponse(response, FakeAPI())
        self.assertEqual(response,
                         resp.subscriptions[0].subscription.subscription)
        self.assertRaises(AttributeError, getattr, resp, 'blah')
        resp_iter = iter(resp)
        self.assertEqual(next(resp_iter),
                         response['SUBSCRIPTIONS'][0])
        self.assertRaises(StopIteration, next, resp_iter)

    @httpretty.activate
    def test_wrapper(self):
        import fastbill
        from mock import Mock

        mock = Mock()

        class ResponseLookAlike(object):
            def __init__(self, status_code):
                self.status_code = status_code

            def __eq__(self, other):
                return self.status_code == other.status_code

        api = fastbill.FastbillWrapper(api_email, api_key,
                                       service_url=api_endpoint,
                                       pre_request=mock.pre_request,
                                       post_request=mock.post_request)

        for method_name, calls in self.TESTCASES.items():
            attribute_name = method_name.replace(".", "_")
            try:
                method = getattr(api, attribute_name)
            except AttributeError:
                if not attribute_name.startswith("_"):
                    raise

            for (filter_by, http_code, response) in calls:
                def request_callback(method, _, headers,
                                     method_name=method_name,
                                     http_code=http_code,
                                     response=response):
                    request = json.loads(method.body.decode('utf8'))
                    request['SERVICE'] = method_name
                    return (http_code, headers, json.dumps({
                        'RESPONSE': response,
                        'REQUEST': request,
                    }, cls=fastbill.jsonencoder.CustomJsonEncoder))

                httpretty.register_uri(httpretty.POST,
                                       api.SERVICE_URL,
                                       body=request_callback)
                params = {'filter': filter_by}

                if http_code == 200:
                    result = method(**params)
                    self.assertEqual(result, response)
                else:
                    self.assertRaises(fastbill.exceptions.FastbillResponseError,
                                      method, **params)

                # The actual payload will look like this.
                payload = params.copy()
                payload.update({
                    'service': method_name,
                    'limit': None,
                    'offset': None,
                    'data': None
                })

                mock.pre_request.assert_called_with(
                    method_name,
                    payload
                )

                mock.post_request.assert_called_with(
                    method_name,
                    payload,
                    ResponseLookAlike(http_code)
                )

    def test_pickle(self):
        import pickle
        import fastbill

        api = fastbill.FastbillWrapper(api_email, api_key,
                                       service_url=api_endpoint,
                                       name="blah")
        response = fastbill.response.FastbillResponse(RESPONSE_DATA, api)
        pickled_response = pickle.dumps(response)
        unpickled_response = pickle.loads(pickled_response)
        self.assertTrue(unpickled_response.api is None)
        self.assertEqual(
            unpickled_response.subscriptions[0].subscription.article_number,
            '1')
        self.assertRaises(
            KeyError,
            lambda: unpickled_response.subscriptions[0].subscription.customer)


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-vv', '--with-doctest'])
