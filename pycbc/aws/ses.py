import logging

import boto3

log = logging.getLogger(__name__)


def send_email(sender, recipient, subject, email_body, bcc_recipients=None):
    ses = boto3.client('ses')
    return ses.send_email(
        Destination={
            'ToAddresses': [recipient],
            'BccAddresses': bcc_recipients or [],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': email_body,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            }
        },
        Source=sender,
    )
