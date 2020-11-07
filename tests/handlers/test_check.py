from unittest.mock import patch

import pytest

from pycbc.handlers import check


@pytest.fixture(autouse=True)
def override_config(config):
    with patch('pycbc.handlers.check.load') as mock:
        mock.return_value = config
        yield mock


@pytest.fixture
def invalid_event():
    return {
        'queryStringParameters': {
            'token': 'invalid'
        }
    }


@pytest.fixture
def event(encrypted_token, branch_id, date, time):
    return {
        'queryStringParameters': {
            'token': encrypted_token,
            'branch_id': branch_id,
            'date': date,
            'time': time,
        }
    }


def test_handler_invalid_token(invalid_event):
    output = check.handler(invalid_event, None)
    assert output['statusCode'] == 200
    assert output['body'] == check._UNAVAILABLE


def test_handler_available(event, branches_times_search_stub):
    output = check.handler(event, None)
    assert output['statusCode'] == 200
    assert output['body'] == check._AVAILABLE


def test_handler_unavailable(event, date, branches_times_search_gen):
    branches_times_search_gen(date, data=[])
    output = check.handler(event, None)
    assert output['statusCode'] == 200
    assert output['body'] == check._UNAVAILABLE
