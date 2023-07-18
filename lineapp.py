from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('A6lbEwifGBQ67vybGFXRFPPuAO9hGxxSkaqi95/yphX52zDJtl6k01L/C4I+0L7oRe46O+jPVP0j6qqOrnus/Rarz8bFDkosFoHa833HoOjmJOWJ/Yvm3ljNiL5DAA8szPupYMEzIm8+i5ve5gZQmQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('3208430c6c18425c7a9bfff70ce3fac0')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


@app.route('/')
def home():
    return 'Hello LINE world.'


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
