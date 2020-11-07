import os
from io import StringIO
from unittest.mock import patch

import pytest

from pycbc import config


@pytest.fixture
def env_vars():
    os.environ['PYCBC_TEST_VAR_1'] = '1'
    os.environ['PYCBC_TEST_VAR_2'] = '2'
    os.environ['ANOTHER_TEST_VAR_3'] = '3'
    yield
    del os.environ['PYCBC_TEST_VAR_1']
    del os.environ['PYCBC_TEST_VAR_2']
    del os.environ['ANOTHER_TEST_VAR_3']


@pytest.fixture
def env_override():
    os.environ['PYCBC_SENDER_EMAIL'] = '1'
    yield
    del os.environ['PYCBC_SENDER_EMAIL']


@pytest.fixture
def no_override_event():
    return {}


@pytest.fixture
def override_all_event():
    return dict(
        config=dict(
            env_prefix='ANOTHER_',
            s3_bucket='test',
            s3_filename='test',
        )
    )


@pytest.fixture
def override_s3_filename():
    os.environ['ANOTHER_S3_FILENAME'] = '1'
    os.environ['ANOTHER_S3_BUCKET'] = '1'
    yield dict(
        config=dict(
            env_prefix='ANOTHER_',
            s3_bucket='test',
        )
    )
    del os.environ['ANOTHER_S3_FILENAME']
    del os.environ['ANOTHER_S3_BUCKET']


@pytest.fixture
def mock_s3():
    with patch('pycbc.config.s3') as s3_mock:
        s3_mock.get_object.return_value = {'Body': StringIO('{}')}
        yield s3_mock
    assert s3_mock.get_object.called


@pytest.fixture
def mock_s3_with_values():
    with patch('pycbc.config.s3') as s3_mock:
        s3_mock.get_object.return_value = {
            'Body': StringIO('{"sender_email": "test"}'),
        }
        yield s3_mock
    assert s3_mock.get_object.called


def test_load_config(no_override_event, mock_s3, env_vars):
    cfg = config.load(no_override_event)
    assert 'test_var_1' in cfg
    assert cfg.test_var_1 == '1'
    assert 'test_var_2' in cfg
    assert cfg.test_var_2 == '2'
    assert 'test_var_3' not in cfg
    mock_s3.get_object.assert_called_once_with(
        Bucket='pycbc',
        Key='pycbc-config.yaml',
    )


def test_load_config_prefix(override_all_event, mock_s3, env_vars):
    cfg = config.load(override_all_event)
    assert 'test_var_1' not in cfg
    assert 'test_var_2' not in cfg
    assert 'test_var_3' in cfg
    assert cfg.test_var_3 == '3'
    mock_s3.get_object.assert_called_once_with(
        Bucket='test',
        Key='test'
    )


def test_load_s3_overrides_default(no_override_event, mock_s3_with_values):
    cfg = config.load(no_override_event)
    assert 'sender_email' in cfg
    assert cfg.sender_email == 'test'


def test_load_env_overrides_default(no_override_event, mock_s3, env_override):
    cfg = config.load(no_override_event)
    assert cfg.sender_email == '1'


def test_load_env_overrides_s3(no_override_event, mock_s3_with_values,
                               env_override):
    cfg = config.load(no_override_event)
    assert cfg.sender_email == '1'


def test_load_event_override(mock_s3_with_values, env_override):
    cfg = config.load(dict(config=dict(sender_email='override')))
    assert cfg.sender_email == 'override'


def test_override_precedence(override_s3_filename, mock_s3_with_values):
    cfg = config.load(override_s3_filename)
    assert cfg.sender_email == 'test'
    mock_s3_with_values.get_object.assert_called_once_with(
        Bucket='test',
        Key='1',
    )


def test_deeply_nested_merge(mock_s3):
    cfg = config.load(
        dict(
            config=dict(
                logging=dict(
                    loggers=dict(
                        pycbc=dict(
                            level='DEBUG')))))
    )
    assert cfg.logging == {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)-15s - %(levelname)-7s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            'pycbc': {
                'handlers': ['console'],
                'level': 'DEBUG',
            }
        }
    }
