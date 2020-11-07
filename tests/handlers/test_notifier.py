from unittest.mock import ANY, patch

import pytest

from pycbc import json
from pycbc.handlers import notifier


@pytest.fixture(autouse=True)
def override_config(config):
    with patch('pycbc.handlers.notifier.load') as mock:
        mock.return_value = config
        yield mock


@pytest.fixture
def event(date_search_output):
    return {
        'Records': [{
            'Sns': {
                'Message': json.dumps(date_search_output),
            },
        }],
    }


@patch('pycbc.handlers.notifier.ses')
@pytest.mark.freeze_time('2020-10-25')
def test_notify_users(ses_mock, event, config, email):
    notifier.handler(event, None)
    ses_mock.send_email.assert_called_once_with(email, email, 'Burnaby Has An Available ICBC Timeslot!',
                                                ANY, bcc_recipients=[email])
