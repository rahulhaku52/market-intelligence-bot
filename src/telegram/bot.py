import os
from telegram import Bot

def send_message(text, chart_path=None):
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    channel = os.environ['TELEGRAM_CHANNEL_ID']
    try:
        if chart_path:
            with open(chart_path, 'rb') as img:
                bot.send_photo(chat_id=channel, photo=img, caption=text)
        else:
            bot.send_message(chat_id=channel, text=text)
    except Exception as e:
        print(f"Telegram error: {e}")
