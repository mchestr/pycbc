from pycbc import json
from pycbc.utils import AttrDict as d


def test_loads():
    assert json.loads('{"test": {"test": 1}}') == d(test=d(test=1))


def test_dumps():
    assert json.dumps({'test': 1}) == '{"test":1}'
