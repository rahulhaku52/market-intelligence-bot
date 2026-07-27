import os
import time
from telegram import Bot
from telegram.error import TelegramError
from tenacity import retry, stop_after_attempt, wait_exponential

# HTML mode er jonno kono escaping dorkar nai
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def send_analysis(message, chart_bytes=None):
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    channel = os.environ['TELEGRAM_CHANNEL_ID']
    try:
        if chart_bytes:
            bot.send_photo(chat_id=channel, photo=chart_bytes, caption=message, parse_mode='HTML')
        else:
            bot.send_message(chat_id=channel, text=message, parse_mode='HTML')
    except TelegramError as e:
        if 'Too Many Requests' in str(e):
            time.sleep(5)
            raise  # retry
        raise
