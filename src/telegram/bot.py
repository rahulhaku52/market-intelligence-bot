import os
import time
from telegram import Bot
from telegram.error import TelegramError
from tenacity import retry, stop_after_attempt, wait_exponential

def send_analysis(message, chart_bytes=None):
    """
    Sends chart (if any) with a short caption, then sends the full message text.
    """
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    channel = os.environ['TELEGRAM_CHANNEL_ID']

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_photo_with_retry(photo_bytes, caption):
        bot.send_photo(chat_id=channel, photo=photo_bytes, caption=caption, parse_mode='HTML')

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_text_with_retry(text):
        bot.send_message(chat_id=channel, text=text, parse_mode='HTML', disable_web_page_preview=True)

    try:
        if chart_bytes:
            # Short caption with ticker name (extract from message, e.g., first bold tag)
            import re
            match = re.search(r'<b>(.*?)</b>', message)
            short_caption = f"📈 {match.group(1)}" if match else "📈 Chart"
            send_photo_with_retry(chart_bytes, short_caption)
            # Send full analysis as a separate message
            send_text_with_retry(message)
        else:
            send_text_with_retry(message)
    except TelegramError as e:
        if 'Too Many Requests' in str(e):
            time.sleep(5)
            raise  # retry
        raise
