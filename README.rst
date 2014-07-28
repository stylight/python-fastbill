python-fastbill
===============

Super thin Python wrapper for Fastbill's HTTP API developed by `STYLIGHT <http://www.stylight.de/>`_.

.. image:: https://travis-ci.org/stylight/python-fastbill.svg?branch=master
    :target: https://travis-ci.org/stylight/python-fastbill


Latest release:
---------------

`fastbill 0.4.3 <https://pypi.python.org/pypi/fastbill/>`_

 * Bugfix release.
 * Calls to potential special methods like __unicode__ would lead to an
   erroneous Fastbill API call.

`fastbill 0.4.2 <https://pypi.python.org/pypi/fastbill/>`_

 * Improved debug logging.
 * **Deprecated `FastbillHttpError` Execption.** Now only `FastbillResponseError`
   will be raised. `FastbillResponseError` will inherit from `FastbillHttpError`
   for the time being, but catching `FastbillHttpError` is deprecated. Use
   `FastbillResponseError` instead.
 * Improved testcase to check for failing API calls as well.

`fastbill 0.4.1 <https://pypi.python.org/pypi/fastbill/>`_

 * **Experimental:** Improved `FastbillResponse` to allow ORM like object
   traversals. Use with caution.
 * Added property `currency` which looks up the proper ISO 4217 currency
   abbreviation when a CURRENCY_CODE integer is present in the response. An
   `AttributeError` will be raised when it's not present.

`fastbill 0.3.1 <https://pypi.python.org/pypi/fastbill/>`_

 * Added support for converting `datetime`, `date`, and `Decimal` types on
   egress. **Note:** Ingress converting is not supported (yet). Builtin numeric
   types have been supported from the start.

Limitations:
------------

* only supports JSON payloads
* doesn't (overly) check for consistency of responses
* doesn't convert date strings to datetime objects

Dependencies:
-------------

* requests

Installation:
-------------

	pip install fastbill

Usage:
------

.. code-block:: python

    from fastbill import FastbillWrapper

    # Construct the api client for Fastbill's automatic API

    client = FastbillWrapper('fastbill_user', 'fastbill_key')

    # You can also specify a service_url, in case you need Fastbill's core API instead:

    core_client = FastbillWrapper('fastbill_user', 'fastbill_key', service_url='endpoint_url')

    # Make requests, e.g. service customer.create

    client.customer_create(data={})

    # Search for customer, subscriptions, etc...

    for customer in client.customer_get(filter={'city': 'Munich'}):
        print customer

    # But you can also see the full result

    result = client.customer_get(filter={'city': 'Munich'})
    print result.keys()

    # Will give you 'CUSTOMERS'
