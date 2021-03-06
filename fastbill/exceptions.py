class FastbillError(Exception):
    """Baseclass for all API errors."""
    pass


class FastbillRequestError(FastbillError):
    """Raised if there are problems with the request."""
    pass


class FastbillHttpError(FastbillError):
    pass


class FastbillResponseError(FastbillHttpError):
    """Raised if Fastbill reports errors in the response."""

    def __init__(self, message, json_response, errors=None):
        super(FastbillResponseError, self).__init__(message)
        self.json_response = json_response
        if errors is None:
            errors = []
        self.errors = errors

    @property
    def broken_fields(self):
        return [error.split(": ")[-1]
                for error in self.errors]
