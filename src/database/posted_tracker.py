import json, os
from datetime import datetime, timedelta
from src.utils.logger import logger

TRACKER_FILE = 'data/posted.json'

def load_posted():
    if not os.path.exists(TRACKER_FILE):
        return {}
    try:
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_posted(data):
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def should_post(ticker, new_trend, new_confidence):
    """
    Returns True if we should post this ticker now.
    Checks:
      - If never posted: True
      - If posted within last 1 hour and trend/confidence similar: False
      - If trend changed or confidence changed by >= 20%: True
      - If last post older than 6 hours: True
    """
    posted = load_posted()
    if ticker not in posted:
        return True
    last = posted[ticker]
    last_time = datetime.fromisoformat(last['timestamp'])
    now = datetime.utcnow()
    delta = now - last_time

    # If last post < 1 hour and no significant change → skip
    if delta < timedelta(hours=1):
        trend_changed = (new_trend != last.get('trend'))
        conf_diff = abs(new_confidence - last.get('confidence', 0))
        if not trend_changed and conf_diff < 20:
            logger.info(f"⏭️ Skipping {ticker}: posted recently with similar analysis")
            return False

    # If last post older than 6 hours, allow (even if no change)
    if delta > timedelta(hours=6):
        return True

    # Otherwise, allow if there's significant change
    trend_changed = (new_trend != last.get('trend'))
    conf_diff = abs(new_confidence - last.get('confidence', 0))
    if trend_changed or conf_diff >= 20:
        logger.info(f"🔄 Significant change for {ticker}, re-posting")
        return True

    return False

def update_posted(ticker, trend, confidence):
    posted = load_posted()
    posted[ticker] = {
        'timestamp': datetime.utcnow().isoformat(),
        'trend': trend,
        'confidence': confidence
    }
    save_posted(posted)
