import sys

PY2 = int(sys.version[0]) == 2
PY26 = PY2 and int(sys.version_info[1]) < 7

if PY26:
    from .ordereddict import OrderedDict
else:
    from collections import OrderedDict
OrderedDict = OrderedDict


if PY2:
    import urlparse
    urlparse = urlparse
    string_types = (str, unicode)
    unicode = unicode
    basestring = basestring
    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()
    builtin_name = '__builtin__'
else:
    import urllib.parse
    urlparse = urllib.parse
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)
    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
    builtin_name = 'builtins'


def encode_if_py2(func):
    """If Python 2.x, return decorated function encoding unicode return value
    to UTF-8; else noop.
    """
    if not PY2:
        return func
    def wrapped(*args, **kwargs):
        ret = func(*args, **kwargs)
        if not isinstance(ret, unicode):
            raise TypeError('Wrapped function must return `unicode`')
        return ret.encode('utf-8', 'ignore')
    return wrapped
