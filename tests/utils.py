import functools

from robobrowser import responses
from robobrowser.compat import iteritems


class ArgCatcher(object):
    """Simple class for memorizing positional and keyword arguments. Used to
    capture responses for mock_responses.

    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class KwargSetter(object):
    """Simple class for memorizing keyword arguments as instance attributes.
    Used to mock requests and responses for testing.

    """
    def __init__(self, **kwargs):
        for key, value in iteritems(kwargs):
            setattr(self, key, value)


def mock_responses(resps):
    """Decorator factory to make tests more DRY. Bundles responses.activate
    with a collection of response rules.

    :param list resps: List of response-formatted ArgCatcher arguments.

    """
    def wrapper(func):
        @responses.activate
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            for resp in resps:
                responses.add(*resp.args, **resp.kwargs)
            return func(*args, **kwargs)
        return wrapped
    return wrapper
