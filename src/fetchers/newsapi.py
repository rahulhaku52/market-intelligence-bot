import os
import requests

def fetch_news(query, from_date, to_date):
    api_key = os.environ['NEWSAPI_KEY']
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': api_key
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json().get('articles', [])
    else:
        return []
