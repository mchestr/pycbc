import json

import pytest
import requests

from pycbc.client import WebBookingClient


@pytest.fixture
def client(mock_responses):
    return WebBookingClient()


def test_service_search(client, service_search_stub, service_search_json):
    data = client.services_search()
    assert data == service_search_json


def test_branches_service_search(client, service_id, branches_service_search_stub, branches_service_search_json):
    data = client.branches_service_search(service_id)
    assert data == branches_service_search_json


def test_branches_dates_search(client, service_id, branch_id, branches_dates_search_stub, branches_dates_search_json):
    data = client.branches_dates_search(service_id, branch_id)
    assert data == branches_dates_search_json


def test_branches_times_search(client, service_id, branch_id, date, branches_times_search_stub,
                               branches_times_search_json):
    data = client.branches_times_search(service_id, branch_id, date)
    assert data == branches_times_search_json


def test_appointments_search(client, user_data, appointments_search_stub, appointments_search_json):
    data = client.appointments_search(user_data.first_name, user_data.last_name, user_data.email, user_data.phone)
    assert data == appointments_search_json
    assert json.loads(appointments_search_stub.calls[0].request.body) == {
        'captcha': False,
        'dob': '',
        'email': user_data.email,
        'externalId': '',
        'firstName': user_data.first_name,
        'lastName': user_data.last_name,
        'phone': user_data.phone
    }


def test_appointment_cancel(client, appointment_id, appointment_cancel_stub):
    data = client.appointment_cancel(appointment_id)
    assert data is None


def test_appointment_reserve(client, appointment_reserve_stub, date, time, appointment_reserve_json, service_id,
                             service_qp_id, service_name, branch_id):
    data = client.appointment_reserve(service_id, service_name, service_qp_id, branch_id, date, time)
    assert data == appointment_reserve_json
    assert json.loads(appointment_reserve_stub.calls[0].request.body) == {
        'custom': json.dumps({
            'peopleServices': [{
                'publicId': service_id,
                'qpId': service_qp_id,
                'adult': 1,
                'name': service_name,
                'child': 0,
            }]
        }, separators=(',', ':')),
        'services': [{
            'publicId': service_id,
        }],
    }


def test_appointment_check_multiple(client, appointment_check_multiple_stub, appointment_check_multiple_ok_json,
                                    service_id, phone, email, date, time):
    data = client.appointment_check_multiple(service_id, date, time, phone, email)
    assert data == appointment_check_multiple_ok_json


def test_appointment_confirm(client, appointment_confirm_stub, appointment_id, service_id, service_qp_id, service_name,
                             date_of_birth, email, first_name, last_name, phone, appointment_confirm_json):
    data = client.appointment_confirm(service_id, service_name, service_qp_id, appointment_id, first_name, last_name,
                                      email, phone, date_of_birth)
    assert data == appointment_confirm_json
    assert json.loads(appointment_confirm_stub.calls[0].request.body) == {
        'captcha': '',
        'custom': json.dumps({
            'peopleServices': [{
                'publicId': service_id,
                'qpId': service_qp_id,
                'adult': 1,
                'name': service_name,
                'child': 0,
            }],
            'totalCost': 0,
            'createdByUser': 'Qmatic Web Booking',
            'customSlotLength': 15,
        }, separators=(',', ':')),
        'customer': {
            'dateOfBirth': date_of_birth,
            'dob': '',
            'email': email,
            'externalId': "",
            'firstName': first_name,
            'lastName': last_name,
            'phone': phone,
        },
        'languageCode': 'en',
        'notes': '',
        'notificationType': '',
        'title': 'Qmatic Web Booking',
    }


def test_configuration(client, configuration_stub, configuration_json):
    data = client.configuration()
    assert data == configuration_json


def test_configuration_bad_response(client, configuration_error_stub):
    with pytest.raises(requests.HTTPError):
        client.configuration()
