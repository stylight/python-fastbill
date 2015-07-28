import pprint as _pp
import six as _six

import requests as _requests

from . import exceptions as _exc
from . import jsonencoder as _jsonencoder
from . import response as _response
from .logger import logger as _logger


class FastbillWrapper(object):
    u"""Wrap Fastbill's HTTP API for easier usage.

    This object doesn't implement any of the concrete API methods, but
    rather implements the common pattern of all these methods.

    The effect is that you can call any Fastbill "services" that are
    available and (given no error on Fastbill's side) it should work.

    You will always be handed the RESPONSE section of the returned data.
    In case of errors a `FastbillException` will be raised.

    """

    SERVICE_URL = "https://automatic.fastbill.com/api/1.0/api.php"

    def __init__(self, email, api_key,
                 session=None,
                 service_url=None,
                 name=None,
                 pre_request=None,
                 post_request=None):
        """
        Args:
            email (str): Your Fastbill user, basically an email address.
            api_key (str): Your Fastbill api_key.

        Kwargs:
            name (str): A value with which you can tag your API instance.

            pre_request (callable): Will be called before any API request.

                Parameters: method, payload

            post_request (callable): Will be called after any API request.

                Parameters: method, payload, http_response

            If you supply pre or post request callbacks, please make sure
            they have the right arity.

        """
        def nop(*args):
            """Do nothing."""
            pass

        if pre_request is not None:
            assert callable(pre_request)
            self._pre_request_callback = pre_request
        else:
            self._pre_request_callback = nop

        if post_request is not None:
            assert callable(post_request)
            self._post_request_callback = post_request
        else:
            self._post_request_callback = nop

        if service_url is not None:
            self.SERVICE_URL = service_url

        _logger.debug("Using endpoint %r", self.SERVICE_URL)

        if session is None:
            session = _requests

        # We use this so clients can identify the API by some arbitrary name.
        # This is useful when dealing with many distinct accounts.
        if name is not None:
            assert isinstance(name, _six.text_type), "Only strings please."
        self.name = name

        self.session = session
        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def __repr__(self):
        return "<%s%s at 0x%x>" % (
            self.__class__.__name__,
            " %s" % self.name if self.name is not None else '',
            id(self)
        )

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError("No such attribute: %s" % name)

        method = name.replace("_", ".")

        def api_method(**kw):
            """Autogenerated method which calls `_request` with the
            correct parameter.

            The service-name will be deduced from the method-name.
            """
            return self._request(method, **kw)
        return api_method

    def _request(self, method, **kw):
        """Do the actual request to Fastbill's API server.

        If successful returns the RESPONSE section the of response, in
        case of an error raises a subclass of FastbillError.
        """
        fb_request = {
            'service': method,
        }
        for key in ['limit', 'offset', 'filter', 'data']:
            fb_request[key] = kw.pop(key, None)

        if kw:
            raise _exc.FastbillRequestError("Unknown arguments: %s" %
                                            ", ".join(kw.keys()))

        data = _jsonencoder.dumps(fb_request)
        _logger.debug("Sending data: %r", data)

        self._pre_request_callback(method, fb_request)
        http_resp = self.session.post(self.SERVICE_URL,
                                      auth=self.auth,
                                      headers=self.headers,
                                      data=data)
        self._post_request_callback(method, fb_request, http_resp)

        body = http_resp.content

        try:
            json_resp = http_resp.json()
        except ValueError:
            _logger.debug("Got data: %r", http_resp.content)
            _abort_http(method, body, http_resp)
        else:
            _logger.debug("Got data: %r", json_resp)

        errors = json_resp['RESPONSE'].get('ERRORS')
        if errors:
            _abort_api(method, json_resp)

        # If Fastbill should ever remove the REQUEST or SERVICE section
        # from their responses, just remove the checks.
        if json_resp['REQUEST']['SERVICE'] != method:
            raise _exc.FastbillError(
                "API Error: Got response from wrong service.")

        return _response.FastbillResponse(json_resp['RESPONSE'], self)


def _abort_api(method, json_resp):
    raise _exc.FastbillResponseError("Error in %s: %r" % (method, json_resp))


def _abort_http(method, body, http_resp):
    """
    >>> class FakeResp(object):
    ...      content = ''
    ...      headers = {'foo': 'bar'}
    ...      status_code = 200
    ...      reason = 'OK'

    >>> _abort("foo.get", FakeResp())
    """
    exc_template = """POST {method} {0.status_code} {0.reason}
Headers:
{headers}
Content:
{0.content!r}
Summary: POST {method} {0.status_code} {0.reason}"""

    headers = _pp.pformat(dict(http_resp.headers), indent=2)


    message = exc_template.format(
        http_resp,
        method=method,
        headers=headers,
    )
    raise _exc.FastbillResponseError(message)
