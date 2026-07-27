import json
from datetime import date, datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Hardcoded NSE holidays for 2025-2026 (update as needed)
NSE_HOLIDAYS = [
    "2025-03-14", "2025-03-31", "2025-04-14", "2025-04-18", "2025-05-01",
    "2025-08-15", "2025-10-02", "2025-10-21", "2025-11-05", "2025-12-25",
    "2026-01-26", "2026-03-14", "2026-03-31", "2026-04-14", "2026-04-18"
]

def load_custom_holidays(filepath='config/nse_holidays.json'):
    try:
        with open(filepath) as f:
            extra = json.load(f)
            return extra.get("holidays", [])
    except:
        return []

ALL_HOLIDAYS = set(NSE_HOLIDAYS + load_custom_holidays())

def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    today_str = now.strftime("%Y-%m-%d")
    if today_str in ALL_HOLIDAYS:
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close

def next_trading_day():
    # return next valid trading day (for expiry calculation)
    d = date.today() + timedelta(days=1)
    while d.weekday() >= 5 or d.isoformat() in ALL_HOLIDAYS:
        d += timedelta(days=1)
    return d