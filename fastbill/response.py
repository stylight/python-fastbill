import six as _six


CURRENCIES = {
    1: u'EUR',
    2: u'GBP',
    3: u'CHF',
    4: u'USD',
    5: u'ZAR',
    6: u'AUD',
    7: u'CAD',
    8: u'PLN',
    9: u'CZK',
    10: u'CNY',
    11: u'HUF',
    12: u'BRL',
    13: u'RON',
    14: u'CVE',
    15: u'DKK',
    16: u'SEK',
    17: u'INR',
    18: u'RUB',
    20: u'HRK',
    22: u'MXN',
    25: u'NOK',
}


class FastbillResponse(dict):

    """Wrap Fastbill's response and help with iterating over the
    returned result."""

    SECTIONS = ['ARTICLES', 'CUSTOMERS', 'INVOICES', 'ITEMS', 'SUBSCRIPTIONS',
                'TEMPLATES', 'EXPENSES']

    def __init__(self, resp, api):
        self.api = api
        super(FastbillResponse, self).__init__(resp)

    def __reduce__(self):
        return self.__class__, (dict(self), None), None, None, None

    @property
    def currency(self):
        try:
            return CURRENCIES[int(self.currency_code)]
        except KeyError as exc:
            raise AttributeError(_six.text_type(exc))

    def __getattr__(self, key):
        key = key.upper()
        if key not in self and self.api is not None:
            id_value = key + "_ID"
            if id_value in self:
                return getattr(self.api, "%s_get" % key.lower())(
                    filter={id_value: self[id_value]}
                )
            else:
                raise AttributeError("%s not found." % key)
        elif type(self[key]) == dict:
            return self.__class__(self[key], self.api)
        elif type(self[key]) == list:
            return [self.__class__(entry, self.api)
                    for entry in self[key]]
        else:
            return self[key]

    def __iter__(self):
        # If we iterate over the result we just want the values
        # and not the stuff we got sent alongside.
        for section in self.SECTIONS:
            if section in self:
                return iter(self[section])

        return iter([])
