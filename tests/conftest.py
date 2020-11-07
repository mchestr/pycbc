import json
from io import StringIO
from unittest.mock import patch

import pytest
import responses
from cryptography.fernet import Fernet

from pycbc import config as pycbc_config
from pycbc.client import WebBookingClient as WBC
from pycbc.utils import AttrDict as d


def load_fixture(name):
    with open(f'tests/fixtures/{name}.json') as f:
        return json.load(f)


@pytest.fixture
def mock_responses():
    with responses.RequestsMock() as resps:
        yield resps


@pytest.fixture
def encrypt_key():
    return Fernet.generate_key().decode('utf-8')


@pytest.fixture
def service_id():
    return 'da8488da9b5df26d32ca58c6d6a7973bedd5d98ad052d62b468d3b04b080ea25'


@pytest.fixture
def branch_id():
    return '53851ce8b410de56e26a0f0d2eda5a3e8d8cf4e05cc1b21af70121f53ef53b5d'


@pytest.fixture
def date():
    return '2021-01-12'


@pytest.fixture
def time():
    return '11:00'


@pytest.fixture
def email():
    return 'test@test.com'


@pytest.fixture
def first_name():
    return 'test'


@pytest.fixture
def last_name():
    return 'test'


@pytest.fixture
def date_of_birth():
    return '1982-10-10'


@pytest.fixture
def phone():
    return '11111111111'


@pytest.fixture
def user_data(first_name, last_name, email, phone, date_of_birth):
    return d({
        'dob': date_of_birth,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
    })


@pytest.fixture
def appointment_id(appointment_reserve_json):
    return appointment_reserve_json['publicId']


@pytest.fixture
def service_qp_id():
    return '27'


@pytest.fixture
def service_name():
    return ('B: Single knowledge test for a new or expired learner’s licence '
            '(45 min)')


@pytest.fixture
def api_gateway():
    return 'https://test.com'


@pytest.fixture
def config(user_data, email, encrypt_key, api_gateway):
    with patch('pycbc.config.s3') as s3_mock:
        s3_mock.get_object.return_value = {'Body': StringIO('{}')}
        yield pycbc_config.load({
            'config': {
                'users': [d(user_data,
                            filters=d(services=['learners'],
                                      days=['saturday', 'sunday'],
                                      branches=['Burnaby']))],
                'encrypt_key': encrypt_key,
                'api_gateway': api_gateway,
                'sender_email': email,
            }})


@pytest.fixture
def service_search_json():
    return load_fixture('service_search')


@pytest.fixture
def branches_service_search_json():
    return load_fixture('branches_service_search')


@pytest.fixture
def branches_dates_search_json():
    return load_fixture('branches_dates_search')


@pytest.fixture
def branches_times_search_json():
    return load_fixture('branches_times_search')


@pytest.fixture
def appointments_search_json():
    return load_fixture('appointments_search')


@pytest.fixture
def appointment_reserve_json():
    return load_fixture('appointment_reserve')


@pytest.fixture
def appointment_check_multiple_ok_json():
    return load_fixture('appointment_check_multiple_ok')


@pytest.fixture
def appointment_check_multiple_fail_json():
    return load_fixture('appointment_check_multiple_fail')


@pytest.fixture
def appointment_confirm_json():
    return load_fixture('appointment_confirm')


@pytest.fixture
def configuration_json():
    return load_fixture('configuration')


@pytest.fixture
def service_search_stub(mock_responses, service_search_json):
    mock_responses.add(responses.GET, WBC.SERVICES_URL,
                       json=service_search_json)
    return mock_responses


@pytest.fixture
def branches_service_search_stub(service_id, branches_service_search_json, mock_responses):
    url = f'{WBC.BRANCHES_AVAILABLE_URL};servicePublicId={service_id}'
    mock_responses.add(responses.GET, url, json=branches_service_search_json)
    return mock_responses


@pytest.fixture
def branches_dates_search_stub(branches_dates_search_json, branch_id, service_id, mock_responses):
    url = (f'{WBC.BRANCH_DATES_URL.format(branch_id=branch_id)}'
           f';servicePublicId={service_id};customSlotLength=15')
    mock_responses.add(responses.GET, url, json=branches_dates_search_json)
    return mock_responses


@pytest.fixture
def branches_times_search_gen(branches_times_search_json, branch_id, service_id, mock_responses):
    def generator(date):
        url = WBC.BRANCH_DATES_TIMES_URL.format(branch_id=branch_id, date=date)
        url += f';servicePublicId={service_id};customSlotLength=15'
        mock_responses.add(responses.GET, url, json=branches_times_search_json)
        return mock_responses

    return generator


@pytest.fixture
def branches_times_search_stub(branches_times_search_gen, date):
    return branches_times_search_gen(date)


@pytest.fixture
def appointments_search_stub(appointments_search_json, user_data, mock_responses):
    url = WBC.APPOINTMENTS_SEARCH_URL
    mock_responses.add(responses.POST, url, json=appointments_search_json)
    return mock_responses


@pytest.fixture
def appointment_cancel_stub(mock_responses, appointment_id):
    url = WBC.APPOINTMENT_URL.format(appointment_id=appointment_id)
    mock_responses.add(responses.DELETE, url)
    return mock_responses


@pytest.fixture
def appointment_reserve_stub(mock_responses, branch_id, date, time, service_id, appointment_reserve_json):
    url = WBC.APPOINTMENT_RESERVE_URL.format(branch_id=branch_id, time=time, date=date)
    url += ';customSlotLength=15'
    mock_responses.add(responses.POST, url, json=appointment_reserve_json)
    return mock_responses


@pytest.fixture
def appointment_check_multiple_stub(mock_responses, phone, email, date, time, service_id,
                                    appointment_check_multiple_ok_json):
    url = WBC.APPOINTMENT_CHECK_MULTIPLE_URL
    url += (f';phone={phone};email={email};servicePublicId={service_id};'
            f'date={date};time={time}')
    mock_responses.add(responses.GET, url, json=appointment_check_multiple_ok_json)
    return mock_responses


@pytest.fixture
def appointment_check_multiple_fail_stub(mock_responses, phone, email, date, time, service_id,
                                         appointment_check_multiple_fail_json):
    url = WBC.APPOINTMENT_CHECK_MULTIPLE_URL
    url += (f';phone={phone};email={email};servicePublicId={service_id};'
            f'date={date};time={time}')
    mock_responses.add(responses.GET, url, json=appointment_check_multiple_fail_json)
    return mock_responses


@pytest.fixture
def appointment_confirm_stub(mock_responses, appointment_id, appointment_confirm_json):
    url = WBC.APPOINTMENT_CONFIRM_URL.format(appointment_id=appointment_id)
    mock_responses.add(responses.POST, url, json=appointment_confirm_json)
    return mock_responses


@pytest.fixture
def configuration_stub(mock_responses, configuration_json):
    url = WBC.CONFIGURATION_URL
    mock_responses.add(responses.GET, url, json=configuration_json)
    return mock_responses


@pytest.fixture
def configuration_error_stub(mock_responses):
    url = WBC.CONFIGURATION_URL
    mock_responses.add(responses.GET, url, status=404)
    return mock_responses
