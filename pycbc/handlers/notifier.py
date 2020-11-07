import logging
import logging.config

import arrow
import calendar

from pycbc import json, templates, token
from pycbc.aws import ses
from pycbc.config import load
from pycbc.utils import AttrDict as d

log = logging.getLogger(__name__)
SERVICE_MAP = {
    '27': 'learners',
}


def handler(event, context):
    config = load(event)
    logging.config.dictConfig(config.logging)
    log.info(f'Event: {event}')

    for record in event['Records']:
        notify_users(config, json.loads(record['Sns']['Message']))


def notify_users(config, input_data):
    for user in _users_by_service(config.users, input_data['qpId']):
        match_and_notify_user(config, user, input_data)


def match_and_notify_user(config, user, input_data):
    user_filters = user.filters

    def _day_filter(d):
        day_name = calendar.day_name[arrow.get(d).weekday()].lower()
        return day_name in user_filters.days

    email_ctx = []
    for branch_name in user_filters.branches:
        if branch_name not in input_data['branches']:
            continue

        branch = input_data['branches'][branch_name]
        available_dates = list(filter(_day_filter, branch['available_dates']))
        if not available_dates:
            continue

        email_ctx.append(dict(branch, available_dates={
            date: branch['available_dates'][date] for date in available_dates
        }))

    if not email_ctx:
        log.info('No available slots after filter')
        return

    encrypted_token = token.encrypt(config.encrypt_key,
                                    d(user=user, service=d(publicId=input_data.publicId,
                                                           name=input_data.name,
                                                           qpId=input_data.qpId)))
    template = templates.generate_email(config, user, email_ctx, encrypted_token)
    subject = f'{len(email_ctx)} Locations Have An Available ICBC Timeslot!'
    if len(email_ctx) == 1:
        subject = f'{email_ctx[0]["name"]} Has An Available ICBC Timeslot!'

    log.info(ses.send_email(config.sender_email, user.email, subject, template, bcc_recipients=[config.sender_email]))


def _users_by_service(users, service):
    yield from (u for u in users
                if SERVICE_MAP[service] in u.filters.services)
