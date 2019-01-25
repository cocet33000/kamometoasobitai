from func import *

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/camome", methods=['POST'])
def camome(URL = None):
    post2one('かもめがいるよ',ID)
    data = request.data.decode('utf-8')
    data = json.loads(data)
    
    if URL != None:
        postimage2one(URL)
    poststamp('11537','52002741')

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json()
    body2 = body.get("events")

    for i in body2:
        print(i)
        ID = i.get("source")["userId"]
        types = i.get("type")

        if(types == "beacon"):
            h = i.get("beacon")
            action = h["type"]
            beacon_action(action, ID)
        
        elif(types == "follow"):
            if ID in USER_LIST:
                print('おかえり')
                post2one('お帰りなさいませ！',ID)
                poststamp('11537','52002736',ID)
            else:
                print('新規ユーザ')
                post2one('初めまして',ID)

        else:
            if(types == "message"):
                h = i.get("message")
                try:
                    text = h["text"]
        
                    if True in (x in text for x in ["かもめ"]):
                        post2one('かもめとあそびたいねー',ID)
        
                    elif True in (x in text for x in ["からす"]):
                        post2one('からすともなかよくね',ID)
                    
                    elif (text == "aaa"):
                        post2one('iii',ID)
                    
                    else:
                        post2one("意味がわかりません", ID)
                        poststamp(11537, 52002756, ID)
                except:
                    None
        
            elif(types == "postback"):
                h = i.get("postback")
                data = h["data"]
        
           #     if(data == TALK_TEMPLETE['M1']['TYPE1']['DATA']): #'ask_youken'
           #         post2admin(TALK_TEMPLETE['M1']['TYPE1']['RET'])
           #         overwride(TALK_TEMPLETE['M1']['TYPE1']['DATA'],'default')
        
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )     
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


