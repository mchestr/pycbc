from unittest.mock import patch, MagicMock

import pytest

from pycbc import json
from pycbc.aws import sns


@pytest.fixture
def mock_sns():
    sns_mock = MagicMock()
    with patch('pycbc.aws.ses.boto3.client') as mock:
        mock.return_value = sns_mock
        yield sns_mock


def test_publish(email, mock_sns):
    sns.publish('test', {})
    mock_sns.publish.assert_called_once_with(
        TopicArn='test',
        Message=json.dumps({}),
    )
