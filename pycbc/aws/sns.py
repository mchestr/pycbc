import json

import boto3


def publish(sns_topic, data):
    sns = boto3.client('sns')
    return sns.publish(
        TopicArn=sns_topic,
        Message=json.dumps(data),
    )
