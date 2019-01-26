import time
from datetime import datetime 
import os
import requests
from PIL import Image
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

import base64
import numpy as np
import io
from util import config_loader
from flask_sqlalchemy import SQLAlchemy


CHANNEL_SECRET = os.getenv('LineMessageAPIChannelSecret')
CHANNEL_ACCESS_TOKEN = os.getenv('LineMessageAPIChannelAccessToken')
DATABASE_URL = os.getenv('DATABASE_URL')


if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if DATABASE_URL is None:
    print('Specify DATABASE_URL as environment variable.')
    sys.exit(1)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

ENDPOINT = config_loader.load('./config/endpoint.yml')
USER_LIST = config_loader.load('./config/user_list.yml')
SITUATION = config_loader.load('./config/situation.yml')

HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer %s' % CHANNEL_ACCESS_TOKEN
}

#
# モデル作成
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(80))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, tasks, user_id):
        self.tasks = tasks
        self.user_id = user_id

    def __repr__(self):
        return '<Task %r>' % self.tasks


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
    print(USER_LIST)
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

def change_situation(situation):
    SITUATION['situation'] = situation
    config_loader.dump(USER_LIST,'config/situation.yml')
    print(SITUATION)

def registration(ID, status):
    USER_LIST[ID] = {}
    USER_LIST[ID]['STATUS'] = status
    USER_LIST[ID]['TIME'] = datetime.now().strftime("%Y/%m/%d %H:%M")
    config_loader.dump(USER_LIST,'config/user_list.yml')
    print(USER_LIST)
    if status == 'ON':
        post2one('通知させていただきます。良い船旅を！', ID)
        poststamp('11537','52002736',ID)
    else:
        post2one('通知機能をオフにします、ごゆっくり。', ID)
        poststamp('11537','52002771 ',ID)


def ask_registration(ID, text='かもめがきたらつうちする？'):
    data = {
        "to": ID,
        "messages": [
            {
                "type": "template",
                "altText": "かもめとあそびたいよね？",
                "template": {
                    "type": "buttons",
                    "text": text,
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
        post2one('ようこそ！さんふらわあへ！！  またのご乗船ありがとうございます！', ID)
        postimage2one('https://www.ferry-sunflower.co.jp/route/osaka-beppu/time/img/img-ship.jpg', ID)
        ask_registration(ID, '前回の船旅はいかがでした？今回もかもめが来たら通知してもよろしいでしょうか？')
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

def nortification_img(image_url):
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
