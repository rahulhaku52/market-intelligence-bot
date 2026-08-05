from datetime import date
from config.settings import SignalStatus
from src.utils.logger import logger

def check_corporate_event_lock(info: dict) -> tuple[bool, str]:
    """
    Checks if a corporate event (e.g. Earnings Result release) is occurring today.
    Returns: (is_locked, reason)
    """
    if not info:
        return False, "NO_EVENT"
        
    try:
        # Check earnings date if available in info
        earnings_timestamp = info.get('earningsTimestamp') or info.get('earningsTimestampStart')
        if earnings_timestamp:
            event_date = date.fromtimestamp(earnings_timestamp)
            today = date.today()
            if event_date == today:
                logger.info(f"🔒 Corporate Event Lock activated: Earnings announcement today ({today.isoformat()})")
                return True, "EARNINGS_RELEASE_TODAY"
    except Exception as e:
        logger.warning(f"Error checking corporate event lock: {e}")
        
    return False, "NO_EVENT"
