def extract_fundamental_quality(info: dict) -> dict:
    if not info:
        return {'quality_score': None, 'metrics': {}}
        
    roe = info.get('returnOnEquity')
    de = info.get('debtToEquity')
    m_margin = info.get('operatingMargins')
    
    available_metrics = {}
    score_points = 0
    total_weight = 0
    
    if roe is not None:
        available_metrics['ROE'] = round(roe * 100, 2)
        if roe > 0.15:
            score_points += 40
        elif roe > 0.10:
            score_points += 25
        total_weight += 40
        
    if de is not None:
        available_metrics['Debt/Equity'] = round(de, 2)
        if de < 0.5:
            score_points += 30
        elif de < 1.0:
            score_points += 15
        total_weight += 30
        
    if m_margin is not None:
        available_metrics['Operating Margin'] = round(m_margin * 100, 2)
        if m_margin > 0.15:
            score_points += 30
        elif m_margin > 0.08:
            score_points += 15
        total_weight += 30
        
    if total_weight == 0:
        return {'quality_score': None, 'metrics': {}}
        
    # Dynamic Weight Normalization
    normalized_score = int((score_points / total_weight) * 100.0)
    return {'quality_score': normalized_score, 'metrics': available_metrics}
