import os
import boto3
import json
import requests


def handler(event, context):
    """
    Send a release event to slack
    """
    TOPIC = os.environ.get('TOPIC_ARN', None)
    SLACK_HOOK = os.environ.get('SLACK_HOOK', None)
    SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', None)

    if TOPIC is None or SLACK_HOOK is None:
        return

    if len(event['Records']) < 1:
        return

    if 'Sns' not in event['Records'][0]:
        return

    message = json.loads(event['Records'][0]['Message'])

    color = {
        'info': 'good',
        'warning': 'warning',
        'error': 'danger'
    }


    slack_msg = {
        "attachments": [
            {
                "fallback": "Event from Coordinator",
                "color": color[ev['event_type']],
                "text": message['message'],
            }
        ]
    }

    if SLACK_CHANNEL:
        slack_msg['channel'] = SLACK_CHANNEL

    resp = requests.post(SLACK_HOOK, json=slack_msg)

    return 'ok'
