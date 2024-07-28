from flask import Flask
from telegram import Bot
import logging

app = Flask(__name__)

# Telegram 配置
TELEGRAM_BOT_TOKEN = '7291139880:AAHPcfpuFQGN-_WOMfKBLRtXKrQft-ycVhc'
TELEGRAM_CHAT_ID = '448345880'

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    # 發送啟動消息到 Telegram
    send_telegram_message("Flask application is starting up!")
    app.run(host='0.0.0.0', port=8080)