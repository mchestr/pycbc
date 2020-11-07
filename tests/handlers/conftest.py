import pytest

from pycbc import token


@pytest.fixture
def date_search_output(branches_times_search_json, service_search_json,
                       branches_service_search_json):
    times_only = [t['time'] for t in branches_times_search_json]
    return dict(
        service_search_json[1],
        branches={
            'Burnaby': dict(branches_service_search_json[1], available_dates={
                '2021-01-06': times_only,
                '2021-01-07': times_only,
                '2021-01-09': times_only,
            })
        }
    )


@pytest.fixture
def encrypted_token(encrypt_key, user_data, service_qp_id, service_name, service_id):
    return token.encrypt(encrypt_key, {
        'user': user_data,
        'service': {
            'name': service_name,
            'qpId': service_qp_id,
            'publicId': service_id,
        }
    })


@pytest.fixture
@pytest.mark.freeze_time('1990-10-25')
def expired_encrypted_token(encrypt_key, user_data, service_qp_id, service_name, service_id):
    return token.encrypt(encrypt_key, {
        'user': user_data,
        'data': {
            'name': service_name,
            'qpId': service_qp_id,
            'publicId': service_id,
        }
    })
