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

:copyright: (c) 2013,2014,2015 Stylight GmbH
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

__version__ = '0.6.0'
__author__ = 'python-fastbill contributors'

from .wrapper import FastbillWrapper
from .exceptions import (
    FastbillResponseError, FastbillRequestError, FastbillError,
    FastbillHttpError)

__all__ = ['FastbillWrapper', 'FastbillResponseError', 'FastbillRequestError',
           'FastbillError', 'FastbillHttpError']
