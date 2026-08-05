def extract_fundamental_growth(info: dict) -> dict:
    if not info:
        return {'growth_score': None, 'metrics': {}}
        
    rev_growth = info.get('revenueGrowth')
    earn_growth = info.get('earningsGrowth')
    
    available_metrics = {}
    score_points = 0
    total_weight = 0
    
    if rev_growth is not None:
        available_metrics['Revenue Growth'] = round(rev_growth * 100, 2)
        if rev_growth > 0.12:
            score_points += 50
        elif rev_growth > 0.05:
            score_points += 30
        total_weight += 50
        
    if earn_growth is not None:
        available_metrics['Earnings Growth'] = round(earn_growth * 100, 2)
        if earn_growth > 0.15:
            score_points += 50
        elif earn_growth > 0.05:
            score_points += 30
        total_weight += 50
        
    if total_weight == 0:
        return {'growth_score': None, 'metrics': {}}
        
    normalized_score = int((score_points / total_weight) * 100.0)
    return {'growth_score': normalized_score, 'metrics': available_metrics}
