from unittest.mock import patch, MagicMock

import pytest

from pycbc.aws import ses


@pytest.fixture
def mock_ses():
    ses_mock = MagicMock()
    with patch('pycbc.aws.ses.boto3.client') as mock:
        mock.return_value = ses_mock
        yield ses_mock


def test_send_email(email, mock_ses):
    ses.send_email(email, email, 'test', 'test', bcc_recipients=[email])
    mock_ses.send_email.assert_called_once_with(
        Destination={
            'ToAddresses': [email],
            'BccAddresses': [email],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': 'test',
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'test',
            }
        },
        Source=email,
    )
