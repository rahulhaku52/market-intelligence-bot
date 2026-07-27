import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')

    if not url or not key:
        print("⚠️ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return None

    # Ensure URL has scheme and no trailing slash
    if not url.startswith('http'):
        url = f'https://{url}'
    url = url.rstrip('/')

    try:
        client = create_client(url, key)
        # We no longer run a health check here; just return the client.
        # Later queries will handle errors gracefully.
        return client
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return None
