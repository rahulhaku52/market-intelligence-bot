def evaluate_overall_risk(confidence: int, atr_pct: float, vix_regime: str, rr: float) -> str:
    risk_points = 0
    if confidence < 70:
        risk_points += 2
    if atr_pct > 3.0:
        risk_points += 2
    if vix_regime == 'HIGH':
        risk_points += 2
    if rr < 2.0:
        risk_points += 1
        
    if risk_points <= 1:
        return 'Low'
    elif risk_points <= 3:
        return 'Medium'
    else:
        return 'High'
