import json

from pycbc.utils import AttrDict as d


def loads(data, **kwargs):
    return json.loads(data, object_hook=d, **kwargs)


def dumps(data, **kwargs):
    return json.dumps(data, separators=(',', ':'), **kwargs)
