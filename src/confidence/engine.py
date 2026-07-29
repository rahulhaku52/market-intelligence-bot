def compute_confidence(tech_score, fund_score, sentiment_score, vol_signal,
                       market_align=50, sector_align=50, earnings_penalty=0, multi_tf_agree=50):
    """
    tech_score : 0-100
    fund_score : 0-100
    sentiment_score : 0-100
    vol_signal : 0-100 (90 for spike, 50 otherwise)
    market_align : 0-100 (default 50)
    sector_align : 0-100 (default 50)
    earnings_penalty : 0-1 (default 0)
    multi_tf_agree : 0-100 (default 50)
    """
    base = (tech_score * 0.35 + fund_score * 0.25 + sentiment_score * 0.15 +
            vol_signal * 0.10 + market_align * 0.05 + sector_align * 0.05 + multi_tf_agree * 0.05)
    base *= (1 - earnings_penalty * 0.2)
    return min(100, max(0, int(base)))
