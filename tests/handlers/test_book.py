from unittest.mock import patch

import pytest

from pycbc import json
from pycbc.handlers import book
from pycbc.utils import AttrDict as d


@pytest.fixture(autouse=True)
def override_config(config):
    with patch('pycbc.handlers.book.load') as mock:
        mock.return_value = config
        yield mock


@pytest.fixture
def event(encrypted_token, config, branch_id, date, time):
    return d(
        config=config,
        queryStringParameters=d(
            token=encrypted_token,
            branch_id=branch_id,
            date=date,
            time=time,
        )
    )


def test_handler(appointment_reserve_stub, appointment_check_multiple_stub, appointment_confirm_stub,
                 configuration_stub, event, appointment_confirm_json):
    output = book.handler(event, None)
    assert output == d(statusCode=200, body=json.dumps(appointment_confirm_json))


def test_handler_existing_appointment(appointment_reserve_stub, appointment_check_multiple_fail_stub,
                                      appointment_confirm_stub, appointments_search_stub, appointment_cancel_stub,
                                      configuration_stub, appointment_confirm_json, event):
    output = book.handler(event, None)
    assert output == d(statusCode=200, body=json.dumps(appointment_confirm_json))
