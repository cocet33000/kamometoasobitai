from func import *


#ビーコンに近ずいた時の検証用エンドポイント 
@app.route("/welcome", methods=['POST'])
def welcome(URL=None):
    ID = 'U7b72725b2f60610adb9c9798949cb360'
    post2one('ようこそ！さんふらわあへ！！  またのご乗船ありがとうございます！', ID)
    postimage2one('https://www.ferry-sunflower.co.jp/route/osaka-beppu/time/img/img-ship.jpg', ID)
    ask_registration(ID, '前回の船旅はいかがでした？今回もかもめが来たら通知してもよろしいでしょうか？')
    return('OK')


#カモメを検知した時のエンドポイント 
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

#カラスを検知した時のエンドポイント 
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


#何も検知していない時のエンドポイント 
@app.route("/etc", methods=['POST'])
def etc(URL=None):
    change_situation('etc')
    return('OK')

#入り口端末用の状態確認エンドポイント
@app.route("/situation", methods=['GET'])
def situation():
    return(SITUATION['situation'])


#メイン
@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json()
    body2 = body.get("events")

    for i in body2:
        print(i)
        ID = i.get("source")["userId"]
        types = i.get("type")
        
        #ビーコン
        if(types == "beacon"):
            h = i.get("beacon")
            action = h["type"]
            beacon_action(action, ID)

        #フォロー
        elif(types == "follow"):
            #if ID in USER_LIST:
            #    print('おかえり')
            #    post2one('おかえり', ID)
            #    ask_registration(ID)
            #else:
            #    print('新規ユーザ')
            #    post2one('はじめまして', ID)
            #    ask_registration(ID)
            
            #データベース確認
            datas = db.session.query(User).all()
            for data in datas:
                print(data.ID)
            registration2(ID, 'ON')
            
            #if not db.session.query(User).filter(User.ID == ID).count():
            #    print('{}さんが入船しました'.format(ID))
            #    post2one('おかえり', ID)
            #    ask_registration(ID)
            #else:
            #    print('新規ユーザ{}'.format(ID))
            #    post2one('はじめまして', ID)
            #    ask_registration(ID)


        #フォロー解除
        elif(types == "unfollow"):
            registration(ID, 'OFF')

        #メッセージ取得時
        else:
            if(types == "message"):
                h = i.get("message")
                try:
                    text = h["text"]

                    if True in (x in text for x in ["教えて", 'おしえて']):
                        registration(ID, 'ON')

                    elif True in (x in text for x in ["だまって", 'うるさい', '黙']):
                        registration(ID, 'OFF')
                    
                    elif True in (x in text for x in ["はい", 'いいえ']):
                        None
                    
                    #その他のメッセージ
                    else:
                        post2one("申し訳ございませんが、お答えできません。", ID)
                        print(ID)
                        poststamp(11537, 52002756, ID)
                except:
                    None

            #ポストバック
            elif(types == "postback"):
                h = i.get("postback")
                data = h["data"]

                #通知オン
                if(data == 'notification'):
                    registration(ID, 'ON')
                    registration2(ID, 'ON')

                #通知オフ
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
