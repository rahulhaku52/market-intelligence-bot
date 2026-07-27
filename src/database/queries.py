from datetime import date, timedelta
from .supabase_client import get_supabase
from src.utils.logger import logger

def should_analyze(ticker, mode, force=False):
    if force:
        return True
    supabase = get_supabase()
    if not supabase:
        # Supabase unavailable → allow analysis
        return True
    try:
        today = date.today()
        res = supabase.table('posted_analysis')\
            .select('*')\
            .eq('ticker', ticker)\
            .eq('category', mode)\
            .gte('expiry_date', today.isoformat())\
            .execute()
        # If table missing, we'll get an exception, but let's handle
        return len(res.data) == 0
    except Exception as e:
        # Table likely doesn't exist yet — allow analysis for now
        logger.warning(f"posted_analysis query failed (table may not exist): {e}")
        return True
