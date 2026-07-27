def compute_confidence(tech_score, fund_score, sentiment_score, vol_signal,
                       market_align, sector_align, earnings_penalty, multi_tf_agree):
    base = (tech_score * 0.30 + fund_score * 0.20 + sentiment_score * 0.15 +
            vol_signal * 0.15 + market_align * 0.10 + sector_align * 0.05 + multi_tf_agree * 0.05)
    # apply earnings penalty
    base *= (1 - earnings_penalty * 0.2)
    return min(100, max(0, int(base)))