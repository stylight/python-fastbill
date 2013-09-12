#!/usr/bin/env python
# encoding: utf-8


api_email = "fastbill@example.com"
api_url = "https://automatic.fastbill.com/api/1.0/api.php"
api_key = "4"


import httpretty
import json


@httpretty.activate
def test_wrapper():
    import fastbill

    TESTCASES = {
        'customer.get': [
            ({'country_code': 'at'}, {'CUSTOMERS': []}),
            ({'country_code': 'de'}, {'CUSTOMERS': [{'NAME': 'Hans'}]}),
        ],

        'subscription.get': [
            ({}, {}),
        ],
    }

    api = fastbill.FastbillAPI(api_url, api_email, api_key)

    for method_name, calls in TESTCASES.items():
        method = getattr(api, method_name.replace(".", "_"))

        for (filter_by, response) in calls:
            def request_callback(method, uri, headers):
                return (200, headers, json.dumps({'RESPONSE': response}))

            httpretty.register_uri(httpretty.POST, api_url,
                                   body=request_callback)
            result = method(filter=filter_by)
            assert result == response


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-vv', '--with-doctest'])
