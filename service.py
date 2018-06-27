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

    ev = json.loads(event['Records'][0]['Sns']['Message'])
    color = {
        'info': 'good',
        'warning': 'warning',
        'error': 'danger'
    }
    
    attachments = []
    slack_msg = {
        'username': 'Release Bot',
        'icon_emoji': ':calendar:'
    }
    emoji = {
        'info': ":small_blue_diamond:",
        'error': ":bangbang:",
        'warning': ":warning:"
    }
    message = f"{emoji[ev['event_type']]} {ev['message']}"
    
    attachment = {
        "fallback": ev['message'],
        "color": color[ev['event_type']],
        "text": message
    }
    
    author = ''
    if ev['release'] is not None:
        author += f":pushpin: {ev['release']}"
        
    if ev['task_service'] is not None:
        author += f" :factory: {ev['task_service']}"
        
    if ev['task'] is not None:
        author += f" :hammer_and_wrench: {ev['task']}"

    # Ignore all task and task service events that are not errors
    if ev['event_type'] != 'error' and ev['task'] is not None and ev['task_service'] is not None:
        return
    
    if author != '':
        attachment["author_name"] = author
        
    attachments.append(
        attachment
    )
    
    slack_msg['attachments'] = attachments


    if 'SLACK_TOKEN' in os.environ and 'SLACK_CHANNEL' in os.environ:
        kms = boto3.client('kms', region_name='us-east-1')
        SLACK_SECRET = os.environ.get('SLACK_TOKEN', None)
        SLACK_TOKEN = kms.decrypt(CiphertextBlob=b64decode(SLACK_SECRET)).get('Plaintext', None).decode('utf-8')
        SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '').split(',')
        SLACK_CHANNEL = [c.replace('#','').replace('@','') for c in SLACK_CHANNEL]

        for channel in SLACK_CHANNEL:
            slack_msg['channel'] = channel

            resp = requests.post('https://slack.com/api/chat.postMessage',
                headers={'Authorization': 'Bearer '+SLACK_TOKEN},
                json=slack_msg)
