#!/usr/bin/env python
# encoding: utf-8

from tornado.escape import json_encode, json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class FastbillAPI(object):
    API_ENDPOINT = "https://automatic.fastbill.com/api/1.0/api.php"

    def __init__(self, email, api_key):
        self.email = email
        self.api_key = api_key
        self.client = AsyncHTTPClient()
        self.headers = {'Content-Type': 'application/json'}

    def _make_request(self, method, **kw):
        request = HTTPRequest(
            url=self.API_ENDPOINT,
            method='POST',
            headers=self.headers,
            auth_username=self.email,
            auth_password=self.api_key,
            body=json_encode({
                'service': method,
            })
        )
        return request

    def _call(self, method, on_success, on_fail, **kw):
        def callback_wrapper(response):
            if response.error:
                return on_fail(response)

            json = json_decode(response.body)
            if json['response.status'] == 'error':
                return on_fail(response)

            return on_success(response)

        request = self._make_request(method, **kw)

        self.client.fetch(request, callback_wrapper)

    def customers(self, on_success, on_fail):
        return self._call('customer.get', on_success, on_fail)

