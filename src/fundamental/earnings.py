def extract_fundamental_earnings(info: dict) -> dict:
    if not info:
        return {'earnings_score': None, 'metrics': {}}
        
    eps = info.get('trailingEps')
    available_metrics = {}
    
    if eps is not None:
        available_metrics['EPS'] = round(eps, 2)
        score = 70 if eps > 0 else 30
        return {'earnings_score': score, 'metrics': available_metrics}
        
    return {'earnings_score': None, 'metrics': {}}
