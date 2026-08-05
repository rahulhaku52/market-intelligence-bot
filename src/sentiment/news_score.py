from textblob import TextBlob
import re

# Indian market finance keywords influence
FINANCE_POS = ['profit', 'growth', 'record', 'jump', 'surge', 'approval', 'dividend', 'buyback', 'upgrade', 'expansion', 'partnership']
FINANCE_NEG = ['loss', 'decline', 'fall', 'crash', 'downgrade', 'fine', 'penalty', 'investigation', 'default', 'lawsuit', 'fraud', 'debt']

def score_articles(articles):
    """
    Calculate sentiment score for a list of articles.
    articles: list of dicts, each with 'title', 'description', and optionally 'source_weight' (0-100).
    Returns score scaled to -30..30 (negative = bearish, positive = bullish).
    """
    if not articles:
        return 0

    total_polarity = 0.0
    total_weight = 0.0

    for a in articles:
        title = a.get('title', '')
        desc = a.get('description', '')
        text = title + " " + desc

        # Base sentiment using TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1

        # Finance-specific keyword boost
        text_lower = text.lower()
        pos_count = sum(1 for word in FINANCE_POS if word in text_lower)
        neg_count = sum(1 for word in FINANCE_NEG if word in text_lower)
        polarity += 0.1 * pos_count - 0.1 * neg_count

        # Clamp polarity to [-1, 1]
        polarity = max(-1.0, min(1.0, polarity))

        # Source weight (default = 50 if not provided)
        weight = a.get('source_weight', 50) / 100.0  # convert to 0-1 scale

        total_polarity += polarity * weight
        total_weight += weight

    if total_weight == 0:
        return 0

    avg = total_polarity / total_weight
    return avg * 30  # scale to -30..30