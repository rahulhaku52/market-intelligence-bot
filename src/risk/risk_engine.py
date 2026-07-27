def compute_risk(conf, atr_pct, volatility, gap, news_risk):
    # news_risk from event classifier (0-10)
    score = 0
    if conf < 50: score += 30
    if atr_pct > 3: score += 20
    if volatility > 0.03: score += 20
    if gap: score += 20
    score += news_risk
    if score < 20: return 'Low'
    elif score < 50: return 'Medium'
    else: return 'High'