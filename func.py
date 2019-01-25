import time 
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

def registration(ID, status):
    USER_LIST[ID] = status
    config_loader.dump(USER_LIST,'config/user_list.yml')

    if status == 'ON':
        post2one('つうちします', ID)
    else:
        post2one('つうちをやめます', ID)


def ask_registration(ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "template",
                "altText": "通知設定",
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
                            "data": "no_notification",
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
        print("becon,enter")
    else:
        print("becon,leave")

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


#def notification(name, ID=):
#    path = ENDPOINT['RASPI2'] + '/images/' + 'comehome.jpg'
#    postimage2one(path,ID)
#    data = {
#        "to": ID,
#        "messages": [
#            {
#                "type": "template",
#                "altText": "来客じの最初の対応",
#                "template": {
#                    "type": "buttons",
#                    "text": name + "さんが来客です。どのように対応されますか",
#                    "actions": [
#                        {
#                            "type": "postback",
#                            "label": "電話をつなぐ",
#                            "text": "電話をつないで",
#                            "data": "line telephone call",
#                        },
#                        {
#                            "type": "postback",
#                            "label": "LINEで対応",
#                            "text": "LINEで対応します",
#                            "data": "line talk",
#                        },
#                        {
#                            "type": "postback",
#                            "label": "対応不可",
#                            "text": "今はいそがしいです",
#                            "data": "impossible",
#                        }
#                    ]
#                }
#            }
#        ]
#    }
#
#    requests.post(
#        ENDPOINT['PUSH_URL'],
#        headers=HEADER,
#        data=json.dumps(data),
#    )
#

#def ask_call(ID):
#    data = {
#        "to": ID,
#        "messages": [
#            {
#                "type": "template",
#                "altText": "スナップショットのテンプレート",
#                "template": {
#                    "type": "buttons",
#                    "text": "LINE通話を始めますか？",
#                    "actions": [
#                        {
#                            "type": "postback",
#                            "label": "はい",
#                            "text": "はい",
#                            "data": "start call",
#                        },
#                        {
#                            "type": "postback",
#                            "label": "いいえ",
#                            "text": "いいえ",
#                            "data": "no",
#                        }
#                    ]
#                }
#            }
#        ]
#    }
#
#    requests.post(
#        ENDPOINT['PUSH_URL'],
#        headers=HEADER,
#        data=json.dumps(data),
#    )
#
