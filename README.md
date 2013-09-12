# stylight-fastbill

Super thin WIP python wrapper for the fastbill API

Limitations:

* currently only supports JSON payloads

Dependencies:

* requests

## Installation

	pip install git+ssh://git@github.com/stylight/stylight-fastbill.git


## Usage

    # Construct the api client

    client = FastbillAPI('api_endpoint_url', 'fastbill_user', 'fastbill_key')

    # Make requests, e.g. service customer.create

    client.customer_create(data={})

    # Search for customer, subscriptions, etc...

    for customer in client.customer_get(filter={'city': 'Munich'}):
        print customer

    # But you can also see the full result

    result = client.customer_get(filter={'city': 'Munich'})
    print result.keys()

    # Will give you 'CUSTOMERS'
