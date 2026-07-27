SOURCE_TRUST = {
    'reuters': 100,
    'bloomberg': 100,
    'economictimes': 95,
    'moneycontrol': 90,
    'livemint': 90,
    'cnbc': 85,
    'zeenews': 70,
    'default': 50
}

def weight_articles(articles):
    weighted = []
    for a in articles:
        source = a.get('source', {}).get('name', '').lower()
        trust = SOURCE_TRUST.get(source, 50)
        a['source_weight'] = trust
        weighted.append(a)
    return weighted