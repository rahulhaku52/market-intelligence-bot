def remove_duplicates(articles, threshold=0.9):
    # Simple Jaccard similarity on titles
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    titles = [a.get('title', '') for a in articles]
    if not titles:
        return articles
    vectorizer = TfidfVectorizer().fit_transform(titles)
    similarity = cosine_similarity(vectorizer)
    to_keep = set()
    discarded = set()
    for i in range(len(articles)):
        if i in discarded: continue
        to_keep.add(i)
        for j in range(i+1, len(articles)):
            if similarity[i,j] > threshold:
                discarded.add(j)
    return [articles[i] for i in to_keep]