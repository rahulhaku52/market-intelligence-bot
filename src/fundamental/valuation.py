def extract_fundamental_valuation(info: dict) -> dict:
    if not info:
        return {'valuation_score': None, 'metrics': {}}
        
    pe = info.get('trailingPE')
    peg = info.get('pegRatio')
    pb = info.get('priceToBook')
    
    available_metrics = {}
    score_points = 0
    total_weight = 0
    
    if pe is not None and pe > 0:
        available_metrics['PE'] = round(pe, 2)
        if pe < 18:
            score_points += 40
        elif pe < 30:
            score_points += 25
        total_weight += 40
        
    if peg is not None and peg > 0:
        available_metrics['PEG'] = round(peg, 2)
        if peg < 1.0:
            score_points += 30
        elif peg < 1.5:
            score_points += 15
        total_weight += 30
        
    if pb is not None and pb > 0:
        available_metrics['P/B'] = round(pb, 2)
        if pb < 3.0:
            score_points += 30
        elif pb < 5.0:
            score_points += 15
        total_weight += 30
        
    if total_weight == 0:
        return {'valuation_score': None, 'metrics': {}}
        
    normalized_score = int((score_points / total_weight) * 100.0)
    return {'valuation_score': normalized_score, 'metrics': available_metrics}
