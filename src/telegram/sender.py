import os
import time
from telegram import Bot
from telegram.error import TelegramError
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import logger

def send_telegram_alert(message: str, chart_bytes=None):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    channel = os.environ.get('TELEGRAM_CHANNEL_ID')
    
    if not token or not channel:
        logger.warning("Telegram credentials not configured. Skipping alert dispatch.")
        return
        
    bot = Bot(token=token)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _send_photo(photo_bytes, caption):
        bot.send_photo(chat_id=channel, photo=photo_bytes, caption=caption, parse_mode='HTML')
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _send_text(text):
        bot.send_message(chat_id=channel, text=text, parse_mode='HTML', disable_web_page_preview=True)

    try:
        if chart_bytes:
            import re
            match = re.search(r'<b>(.*?)</b>', message)
            caption = f"📈 {match.group(1)}" if match else "📈 Signal Chart"
            _send_photo(chart_bytes, caption)
            _send_text(message)
        else:
            _send_text(message)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
