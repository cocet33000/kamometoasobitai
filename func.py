import time
from datetime import datetime 
import os
import requests
import json
import sys
from flask import Flask, request,jsonify
from linebot import ( LineBotApi,
    WebhookHandler
)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

from util import config_loader
import io

app = Flask(__name__)

CHANNEL_SECRET = os.getenv('LineMessageAPIChannelSecret')
CHANNEL_ACCESS_TOKEN = os.getenv('LineMessageAPIChannelAccessToken')

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

ENDPOINT = config_loader.load('./config/endpoint.yml')
USER_LIST = config_loader.load('./config/user_list.yml')

HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer %s' % CHANNEL_ACCESS_TOKEN
}

def renew():
    print(USER_LIST)
    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    now = datetime.strptime(now, "%Y/%m/%d %H:%M")
    for user in USER_LIST:
        date = datetime.strptime(USER_LIST[user]['TIME'], '%Y/%m/%d %H:%M')
        diff = now - date
        print(diff)
        try:
            diff_hour = diff.hour
            USER_LIST[user]['STATUS'] = 'OFF'
            
        except:
            None


def nortification(text):
    renew()
    IDs = []
    for user in USER_LIST:
        if USER_LIST[user]['STATUS'] == 'ON':
            IDs.append(user)
    data = {
        "to": IDs,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ]
    }

    res = requests.post(
        ENDPOINT['MULTICAST'],
        data=json.dumps(data),
        headers=HEADER,
    )
    print(res)

def registration(ID, status):
    USER_LIST[ID] = {}
    USER_LIST[ID]['STATUS'] = status
    USER_LIST[ID]['TIME'] = datetime.now().strftime("%Y/%m/%d %H:%M")
    config_loader.dump(USER_LIST,'config/user_list.yml')
    print(USER_LIST)
    if status == 'ON':
        post2one('つうちします', ID)
        poststamp('11537','52002736',ID)
    else:
        post2one('つうちをやめます', ID)


def ask_registration(ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "template",
                "altText": "かもめとあそびたいよね？",
                "template": {
                    "type": "buttons",
                    "text": "かもめがきたらつうちする？",
                    "actions": [
                        {
                            "type": "postback",
                            "label": "はい",
                            "text": "はい",
                            "data": "notification",
                        },
                        {
                            "type": "postback",
                            "label": "いいえ",
                            "text": "いいえ",
                            "data": "no notification",
                        }
                    ]
                }
            }
        ]
    }

    requests.post(
        ENDPOINT['PUSH_URL'],
        headers=HEADER,
        data=json.dumps(data),
    )

def beacon_action(action, ID):
    if(action == "enter"):
        post2one('ようこそ！さんふらわあへ！！！', ID)
        ask_registration(ID)
        print("becon,enter")
   # else:
   #     ask_registration(ID)
   #     print("becon,leave")

def poststamp(a, b, ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": 'sticker',
                'packageId': a,
                'stickerId': b,
            }
        ]
    }

    res = requests.post(
        ENDPOINT['POST'],
        headers=HEADER,
        data=json.dumps(data),
    )
    print(res)

def nortification_img(image_url, ID):
    IDs = []
    for user in USER_LIST:
        if USER_LIST[user]['STATUS'] == 'ON':
            IDs.append(user)
    
    data = {
        "to": IDs,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url,
            }
        ]
    }

    res = requests.post(
        ENDPOINT['MULTICAST'],
        data=json.dumps(data),
        headers=HEADER,
    )
    print(res)

def postimage2one(image_url, ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url,
            }
        ]
    }

    res = requests.post(
        ENDPOINT['POST'],
        data=json.dumps(data),
        headers=HEADER,
    )
    print(res)


def post2one(post_text, ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "text",
                "text": post_text
            }
        ]
    }
    
    res = requests.post(
        'https://api.line.me/v2/bot/message/push',
        headers=HEADER,
        data=json.dumps(data),
    )
    print(res)
