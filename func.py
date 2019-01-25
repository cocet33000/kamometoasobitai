import time 
import os
import requests
import json
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

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')


ENDPOINT = config_loader.load('./config/endpoint.yml')
#IMAGE_FILES = config_loader.load('./config/images.yml')
#TALK_TEMPLETE = config_loader.load('./config/talk_templete.yml')
#PASSWORD_TEMPLETE = config_loader.load('./config/password.yml')
#LOGIN = config_loader.load('./config/login.yml')
#PASS_SUCCESS = config_loader.load('./config/pass_success.yml')
#TEMPLETE = config_loader.load('./config/templete.yml')

#USER_LIST = config_loader.load('./config/user_list.yml')

HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer %s' % CHANNEL_ACCESS_TOKEN
}

def beacon_action(action, ID):
    if(action == "enter"):
        print("becon,enter")
        if(ID in USER_LIST):
            name = USER_LIST[ID]
            if(ID != ADMIN_ID):
                # to ADMIN
                post2admin(name + "が帰宅しました")
                poststamp('11537','52002741')
                # to YOUSER
                post2one("おかえりなさい、待ってたよ！！", ID)
                poststamp('11537','52002736',ID)
            else:
                # to ADMIN
                post2one(name + "おかえりなさいませ。今日は荷物が届いていますよ。", ID)
                poststamp('11537','52002736',ID)

    else:
        print("becon,leave")
        if(ID in USER_LIST):
            name = USER_LIST[ID]
            # to ADMIN
            post2admin(name + "がおでかけみたいです")
            poststamp('11537','52002741')
            # to YOUSER
            post2one("行ってらっしゃい！良い1日になりますように", ID)
            poststamp('11537','52002736',ID)

def poststamp(a, b, ID = ADMIN_ID):
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

    requests.post(
        ENDPOINT['PUSH_URL'],
        headers=HEADER,
        data=json.dumps(data),
    )

#def okaeri(ID):

def postimage2one(image_url, ID = ADMIN_ID):
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

    requests.post(
        ENDPOINT['POST'],
        data=json.dumps(data),
        headers=HEADER,
    )


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

    requests.post(
        ENDPOINT['POST'],
        data=json.dumps(data),
        headers=HEADER,
    )


#def notification(name, ID=ADMIN_ID):
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

def ask_call(ID):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "template",
                "altText": "スナップショットのテンプレート",
                "template": {
                    "type": "buttons",
                    "text": "LINE通話を始めますか？",
                    "actions": [
                        {
                            "type": "postback",
                            "label": "はい",
                            "text": "はい",
                            "data": "start call",
                        },
                        {
                            "type": "postback",
                            "label": "いいえ",
                            "text": "いいえ",
                            "data": "no",
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

