import sys

PY2 = int(sys.version[0]) == 2
PY26 = PY2 and int(sys.version_info[1]) < 7

if PY26:
    from .ordereddict import OrderedDict
else:
    from collections import OrderedDict
