import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set in environment variables.")
    
    # Ensure URL has scheme
    if not url.startswith('http'):
        url = f'https://{url}'
    
    # Remove trailing slash if present
    url = url.rstrip('/')
    
    return create_client(url, key)
