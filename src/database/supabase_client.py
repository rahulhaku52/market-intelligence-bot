import os
import sys
from supabase import create_client, Client
from src.utils.logger import logger

def get_supabase() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')

    if not url or not key:
        logger.error("❌ SUPABASE_URL or SUPABASE_SERVICE_KEY missing!")
        sys.exit(1)

    # Ensure URL has scheme
    if not url.startswith('http'):
        url = f'https://{url}'

    url = url.rstrip('/')

    try:
        client = create_client(url, key)
        # Quick health check: try a simple query (public schema exists by default)
        client.table('watchlist').select('ticker').limit(1).execute()
        logger.info("✅ Supabase connection verified.")
        return client
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        logger.error("Please check your SUPABASE_URL and project status.")
        # Don't exit, allow the rest of pipeline to run (backtesting will be skipped gracefully)
        return None
