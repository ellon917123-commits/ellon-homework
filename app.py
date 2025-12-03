from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)

# ================= 設定區 =================
# 建議將這些敏感資訊放在環境變數中，這裡為了教學方便直接填入
LINE_CHANNEL_ACCESS_TOKEN = 'YUeziHSnV8Jt70QRKQiDHLRnXpuAk437fq+HNllSeCYXOVq6paCT0Ry1PI+ih4QhHLBOFC3x9UCR/qxyQuvGHyRLI1NCMf8Z+A56WTfpLHCksNofHDxn5ifnqJHlk/Nz8zasnGl+sU8dWjhiW3x/0QdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'c50431f1d96b29752fdb212a623afd58'
GEMINI_API_KEY = 'AIzaSyA3ebaw7r1hYrjf_tciUX1ATo62mERu_Vg'
# =========================================

# 設定 LINE Bot
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 設定 Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')  # 使用 gemini-pro 模型


@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature header 值
    signature = request.headers['X-Line-Signature']

    # 獲取 request body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # 1. 將使用者訊息傳送給 Gemini
        response = model.generate_content(user_message)
        reply_text = response.text

        # 2. 將 Gemini 的回應回傳給 LINE 使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        # 錯誤處理
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，我現在無法思考 (API Error)")
        )
        print(f"Error: {e}")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)