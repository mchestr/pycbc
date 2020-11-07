import logging
import logging.config

from cryptography.fernet import InvalidToken

from pycbc import client, json, token
from pycbc.config import load
from pycbc.utils import AttrDict as d

log = logging.getLogger(__name__)


def handler(event, context):
    config = load(event)
    logging.config.dictConfig(config.logging)

    try:
        query_params = event['queryStringParameters']
        query_token = query_params.pop('token')

        payload = token.decrypt(config.encrypt_key, query_token, ttl=3600)
    except InvalidToken:
        return {
            'statusCode': 400,
            'body': 'token expired',
        }
    except Exception as exc:
        log.exception(exc)
        return {
            'statusCode': 401,
            'body': 'UNAUTHORIZED',
        }
    log.info(f'Payload: {payload}')

    branch = d(branch_id=query_params['branch_id'],
               date=query_params['date'],
               time=query_params['time'])
    try:
        reservation = reserve(payload.service, branch, payload.user)
        return {
            'statusCode': 200,
            'body': json.dumps(reservation),
        }
    except Exception as exc:
        log.exception(exc)
        return {
            'statusCode': 500,
            'body': 'failed to book appointment',
        }


def reserve(service, branch, user):
    pycbc = client.WebBookingClient()

    pycbc.configuration()
    reservation = pycbc.appointment_reserve(service.publicId, service.name, service.qpId, **branch)
    check = pycbc.appointment_check_multiple(service.publicId, branch.date, branch.time, user.phone, user.email)
    if check.message != 'MULTIPLE_OK':
        appointments = pycbc.appointments_search(user.first_name, user.last_name, user.email, user.phone)
        log.info(f'Existing appointments: {appointments}')
        pycbc.appointment_cancel(appointments[0].publicId)
        log.info(f'Appointment cancelled: {appointments[0]}')

    date_of_birth = user.pop('dob')
    return pycbc.appointment_confirm(service.publicId, service.name, service.qpId, reservation.publicId,
                                     date_of_birth=date_of_birth, **user)
