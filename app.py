from func import *

@app.route("/welcome", methods=['POST'])
def welcome(URL=None):
    ID = 'U7b72725b2f60610adb9c9798949cb360'
    post2one('ようこそ！さんふらわあへ！！  またのご乗船ありがとうございます！', ID)
    postimage2one('https://www.ferry-sunflower.co.jp/route/osaka-beppu/time/img/img-ship.jpg', ID)
    ask_registration(ID, '前回の船旅はいかがでした？今回もかもめが来たら通知してもよろしいでしょうか？')
    
    return('OK')

@app.route("/kamome", methods=['POST'])
def kamome(URL=None):
    change_situation('kamome')
    data = request.data.decode('utf-8')
    data = json.loads(data)
    im = np.array(data)
    pil_img = Image.fromarray(im.astype('uint8'))
    pil_img.save('save.png')

    nortification('かもめがいるよーーー！！いそいでみにきてーー！！')
    nortification_img('https://camometoasobitai.herokuapp.com/save.png')
    
    return('OK')


@app.route("/karasu", methods=['POST'])
def karasu():
    change_situation('karasu')
    data = request.data.decode('utf-8')
    data = json.loads(data)
    im = np.array(data)
    pil_img = Image.fromarray(im.astype('uint8'))
    pil_img.save('save.png')

    nortification('か、からすがいるよ！')
    nortification_img('https://camometoasobitai.herokuapp.com/save.png')
    return('OK')


@app.route("/etc", methods=['POST'])
def etc(URL=None):
    change_situation('etc')
    return('OK')


@app.route("/situation", methods=['GET'])
def situation():
    return(SITUATION['situation'])


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
                post2one('おかえり', ID)
                ask_registration(ID)
            else:
                print('新規ユーザ')
                post2one('はじめまして', ID)
                ask_registration(ID)

        elif(types == "unfollow"):
            registration(ID, 'OFF')

        else:
            if(types == "message"):
                h = i.get("message")
                try:
                    text = h["text"]

                    if True in (x in text for x in ["教えて", 'おしえて']):
                        registration(ID, 'ON')

                    elif True in (x in text for x in ["だまって", 'うるさい', '黙']):
                        registration(ID, 'OFF')

                    ## else:
                    #    post2one("意味がわかりません", ID)
                    #    print(ID)
                    #    poststamp(11537, 52002756, ID)
                except:
                    None

            elif(types == "postback"):
                h = i.get("postback")
                data = h["data"]

                if(data == 'notification'):
                    registration(ID, 'ON')

                elif(data == 'no notification'):
                    registration(ID, 'OFF')

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
