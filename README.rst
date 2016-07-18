python-fastbill
===============

Super thin Python wrapper for Fastbill's HTTP API developed by `STYLIGHT <http://www.stylight.de/>`_.

.. image:: https://travis-ci.org/stylight/python-fastbill.svg?branch=master
    :target: https://travis-ci.org/stylight/python-fastbill

.. image:: https://img.shields.io/pypi/pyversions/fastbill.svg

.. image:: https://img.shields.io/pypi/dm/fastbill.svg
    :target: https://pypi.python.org/pypi/fastbill

Latest release:
---------------

`fastbill 0.7.2  <https://pypi.python.org/pypi/fastbill/>`_

 * Add configurable timeout to all API calls. The default timeout is 1 minute.
   *This could lead to unexpected timeout exceptions, you'll need to handle.*

`fastbill 0.7.1 <https://pypi.python.org/pypi/fastbill/>`_

 * Bugfix release for name parameter.

`fastbill 0.7.0 <https://pypi.python.org/pypi/fastbill/>`_

 * Warning: This release has a bug. The 'name' parameter will break on str
   types on Python2. Use 0.7.1 instead.
 * *Potentially breaking change*: Restructure fastbill module into package
   with each component having it's own module. Your imports may break.

`fastbill 0.6.1 <https://pypi.python.org/pypi/fastbill/>`_

 * Added mock library to setup.py

`fastbill 0.6.0 <https://pypi.python.org/pypi/fastbill/>`_

 * *Breaking change*: Don't throw a KeyError, but rather an AttributeError on FastbillResponse.currency property
 * Add pre- and post-request callbacks

`fastbill 0.5.2 <https://pypi.python.org/pypi/fastbill/>`_

 * Added NOK to CURRENCIES dict.

`fastbill 0.5.1 <https://pypi.python.org/pypi/fastbill/>`_

 * Support pickling of `FastbillResponse` objects. The link to the API connection
   will not be pickled though. API credentials will also not be pickled.

`fastbill 0.5.0 <https://pypi.python.org/pypi/fastbill/>`_

 * Introduce `name` parameter to better distinguish `FastbillWrapper` instances.

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


Limitations:
------------

* only supports JSON payloads
* doesn't (overly) check for consistency of responses
* doesn't convert date strings to datetime objects

Dependencies:
-------------

* requests
* six (for Python 2/3 compatibility)

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
