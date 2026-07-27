import os
import time
from telegram import Bot
from telegram.error import TelegramError
from tenacity import retry, stop_after_attempt, wait_exponential
import re

def escape_markdown(text):
    # MarkdownV2 escape
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def send_analysis(message, chart_bytes=None):
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    channel = os.environ['TELEGRAM_CHANNEL_ID']
    safe_message = escape_markdown(message)
    try:
        if chart_bytes:
            bot.send_photo(chat_id=channel, photo=chart_bytes, caption=safe_message, parse_mode='MarkdownV2')
        else:
            bot.send_message(chat_id=channel, text=safe_message, parse_mode='MarkdownV2')
    except TelegramError as e:
        if 'Too Many Requests' in str(e):
            time.sleep(5)
            raise  # retry
        raise
