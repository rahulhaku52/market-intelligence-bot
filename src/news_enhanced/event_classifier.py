KEYWORDS = {
    'earnings': ['profit', 'revenue', 'eps', 'net income', 'quarterly'],
    'dividend': ['dividend', 'record date', 'payment'],
    'corp_action': ['bonus', 'split', 'rights', 'buyback'],
    'rbi_policy': ['rbi', 'repo rate', 'monetary policy', 'inflation'],
    'geopolitical': ['war', 'election', 'tariff', 'sanction'],
}

def classify_event(article):
    title = (article.get('title','') + ' ' + article.get('description','')).lower()
    for category, words in KEYWORDS.items():
        if any(word in title for word in words):
            return category
    return 'general'