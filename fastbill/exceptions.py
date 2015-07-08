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
    pass
