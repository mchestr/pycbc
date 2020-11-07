from unittest.mock import ANY, patch

import pytest

from pycbc.handlers import notifier


@patch('pycbc.handlers.notifier.ses')
@pytest.mark.freeze_time('2020-10-25')
def test_notify_users(ses_mock, date_search_output, config, email):
    notifier.notify_users(config, date_search_output)
    ses_mock.send_email.assert_called_once_with(email, email, 'Burnaby Has An Available ICBC Timeslot!',
                                                ANY, bcc_recipients=[email])
