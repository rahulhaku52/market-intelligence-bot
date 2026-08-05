def compute_dynamic_confluence(
    tech_score: float,
    mtf_score: float,
    structure_score: float,
    volume_score: float,
    sector_score: float,
    market_breadth_score: float,
    fund_quality_score: float = None,
    fund_growth_score: float = None,
    fund_val_score: float = None,
    news_sentiment_score: float = None
) -> dict:
    """
    Computes dynamic confluence score.
    If optional metrics (fundamentals, news) are None, their weights are omitted
    and remaining available weights are re-normalized to 100%.
    """
    weights = {
        'tech': 0.20,
        'mtf': 0.15,
        'structure': 0.15,
        'volume': 0.15,
        'sector': 0.10,
        'breadth': 0.10,
        'fund_quality': 0.05,
        'fund_growth': 0.04,
        'fund_val': 0.03,
        'news': 0.03
    }
    
    scores = {
        'tech': tech_score,
        'mtf': mtf_score,
        'structure': structure_score,
        'volume': volume_score,
        'sector': sector_score,
        'breadth': market_breadth_score,
        'fund_quality': fund_quality_score,
        'fund_growth': fund_growth_score,
        'fund_val': fund_val_score,
        'news': news_sentiment_score
    }
    
    weighted_sum = 0.0
    active_weight_sum = 0.0
    
    for key, weight in weights.items():
        val = scores[key]
        if val is not None:
            weighted_sum += val * weight
            active_weight_sum += weight
            
    if active_weight_sum == 0:
        return {'confluence_score': 0, 'active_weight_pct': 0.0}
        
    # Weight Re-Normalization
    final_score = int(weighted_sum / active_weight_sum)
    active_weight_pct = round(active_weight_sum * 100.0, 1)
    
    return {
        'confluence_score': max(0, min(100, final_score)),
        'active_weight_pct': active_weight_pct
    }
