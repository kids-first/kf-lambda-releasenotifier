import os
import json
import re
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
    emoji = emoji_from_message(ev['message'])
    emoji = emoji[ev['event_type']] if emoji is None else emoji
    message = f"{emoji} {ev['message']}"
    
    attachment = {
        "fallback": ev['message'],
        "color": color[ev['event_type']],
        "text": message
    }
    
    author = ''
    author_link = ''
    if ev['release'] is not None:
        author += f":pushpin: {ev['release']}"
        if '-dev' in context.function_name:
            author_link = 'https://kf-ui-release-coordinator-dev.kids-first.io/releases/'
        elif '-qa' in context.function_name:
            author_link = 'https://kf-ui-release-coordinator-qa.kids-first.io/releases/'
        else:
            author_link = 'https://kf-ui-release-coordinator.kids-first.io/releases/'
        author_link += ev['release']
        
    if ev['task_service'] is not None:
        author += f" :factory: {ev['task_service']}"
        
    if ev['task'] is not None:
        author += f" :hammer_and_wrench: {ev['task']}"
    

    # Ignore all task and task service events that are not errors
    if ev['event_type'] != 'error' and ev['task'] is not None and ev['task_service'] is not None:
        return
    
    if author != '':
        attachment["author_name"] = author
    if author_link != '':
        attachment['author_link'] = author_link
        
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

def emoji_from_message(msg):
    p = r'^.*from (\w+) to (\w+)$'
    m = re.match(p, msg)
    trans = {
        'initializing': ':clock1:',
        'running': ':athletic_shoe:',
        'staged': ':warning:',
        'publishing': ':recycle:',
        'published': ':white_check_mark:',
        'canceling': ':double_vertical_bar:',
        'canceled': ':no_entry_sign:',
        'failed': ':exclamation:'
    }
    if m and len(m.groups()) == 2:
        fr = m.groups()[0]
        to = m.groups()[1]
        if to not in trans:
            return ':blue_diamond:'
        return trans[to]


