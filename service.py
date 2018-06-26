import os
import json
import boto3
from base64 import b64decode
from botocore.vendored import requests


def handler(event, context):
    """
    Send a release event to slack
    """
    if 'Records' not in event or  len(event['Records']) < 1:
        return

    if 'Sns' not in event['Records'][0]:
        return

    message = json.loads(event['Records'][0]['Sns']['Message'])

    color = {
        'info': 'good',
        'warning': 'warning',
        'error': 'danger'
    }


    if 'SLACK_TOKEN' in os.environ and 'SLACK_CHANNEL' in os.environ:
        kms = boto3.client('kms', region_name='us-east-1')
        SLACK_SECRET = os.environ.get('SLACK_TOKEN', None)
        SLACK_TOKEN = kms.decrypt(CiphertextBlob=b64decode(SLACK_SECRET)).get('Plaintext', None).decode('utf-8')
        SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '').split(',')
        SLACK_CHANNEL = [c.replace('#','').replace('@','') for c in SLACK_CHANNEL]

        for channel in SLACK_CHANNEL:
            slack_msg = {
                'username': 'Release Bot',
                'icon_emoji': ':calendar:',
                'channel': channel,
                'attachments': [
                    {
                        "fallback": message['message'],
                        #"color": color[ev['event_type']],
                        "text": message['message'],
                    }
                ]
            }

            resp = requests.post('https://slack.com/api/chat.postMessage',
                headers={'Authorization': 'Bearer '+SLACK_TOKEN},
                json=slack_msg)
