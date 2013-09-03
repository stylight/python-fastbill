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


