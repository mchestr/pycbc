import pytest
from cryptography.fernet import Fernet

from pycbc import token


@pytest.fixture
def key():
    return Fernet.generate_key().decode('utf-8')


def test_encryption(key):
    input_data = {
        'some': {
            'keys': {
                'in': {
                    'nested': 1
                },
            },
        },
        'dict': 2,
    }
    encrypted = token.encrypt(key, input_data)
    assert encrypted
    assert type(encrypted) is str
    decrypted = token.decrypt(key, encrypted)
    assert decrypted == input_data
