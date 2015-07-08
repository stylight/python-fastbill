import datetime
import decimal
import json

decimal_types = (decimal.Decimal,)

try:
    import cdecimal
    decimal_types += (cdecimal.Decimal,)
    decimal = cdecimal
except ImportError:
    pass


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal_types):
            return str(o)
        elif type(o) == datetime.date:
            return o.strftime('%Y-%m-%d')
        elif type(o) == datetime.datetime:
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super(CustomJsonEncoder, self).default(o)


def dumps(value):
    return json.dumps(value, cls=CustomJsonEncoder)
