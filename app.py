from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)

# ================= 設定區 =================
# 從環境變數中讀取敏感資訊
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 檢查是否有任何一個金鑰未設定
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, GEMINI_API_KEY]):
    # 可以在這裡加入更詳細的日誌記錄或錯誤處理
    print("錯誤：部分或全部的環境變數（LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, GEMINI_API_KEY）未設定。")
    # 根據您的需求，您可能會希望在這裡直接退出程式
    # import sys
    # sys.exit(1)
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