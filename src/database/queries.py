from datetime import date, timedelta
from .supabase_client import get_supabase

def should_analyze(ticker, mode, force=False):
    if force:
        return True
    supabase = get_supabase()
    today = date.today()
    # Check if same ticker+mode was posted recently with active expiry
    res = supabase.table('posted_analysis')\
        .select('*')\
        .eq('ticker', ticker)\
        .eq('category', mode)\
        .gte('expiry_date', today.isoformat())\
        .execute()
    if len(res.data) > 0:
        return False
    # Also check if there is a recent signal (e.g., breaking news within last 6 hours) — can be extended
    return True